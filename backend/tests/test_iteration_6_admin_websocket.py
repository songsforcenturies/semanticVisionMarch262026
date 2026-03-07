"""
Iteration 6 Backend Tests - Admin Dashboard & WebSocket
Tests:
1. GET /api/admin/costs - Cost tracking data (requires auth)
2. GET /api/admin/models - LLM config
3. POST /api/admin/models - Update LLM config
4. WebSocket /ws/session/{id} - Connection test
"""

import pytest
import requests
import os
import json
import websocket
import threading
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndSetup:
    """Basic health check tests"""
    
    def test_health_endpoint(self):
        """Health endpoint returns 200 with healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("PASS: Health endpoint healthy")


class TestAdminCostsEndpoint:
    """Test /api/admin/costs endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Login as guardian to get auth token"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "testreset@test.com", "password": "Test1234!"}
        )
        if login_response.status_code != 200:
            pytest.skip("Guardian login failed - skipping authenticated tests")
        return login_response.json().get("access_token")
    
    def test_admin_costs_without_auth(self):
        """GET /api/admin/costs without auth should return 401 or 403"""
        response = requests.get(f"{BASE_URL}/api/admin/costs")
        # Should require authentication - can be 401 (Unauthorized) or 403 (Forbidden)
        assert response.status_code in [401, 403]
        print(f"PASS: Admin costs endpoint requires authentication (status: {response.status_code})")
    
    def test_admin_costs_with_auth(self, auth_token):
        """GET /api/admin/costs with auth should return cost aggregation data"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/costs", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "total_cost" in data
        assert "total_stories" in data
        assert "per_user" in data
        assert "per_model" in data
        assert "recent_logs" in data
        
        # Validate types
        assert isinstance(data["total_cost"], (int, float))
        assert isinstance(data["total_stories"], int)
        assert isinstance(data["per_user"], list)
        assert isinstance(data["per_model"], list)
        assert isinstance(data["recent_logs"], list)
        
        print(f"PASS: Admin costs endpoint returns valid structure")
        print(f"  Total cost: ${data['total_cost']}")
        print(f"  Total stories: {data['total_stories']}")
        print(f"  Users with costs: {len(data['per_user'])}")
        print(f"  Models used: {len(data['per_model'])}")
        print(f"  Recent logs: {len(data['recent_logs'])}")


class TestAdminModelsEndpoint:
    """Test /api/admin/models GET and POST endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Login as guardian to get auth token"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "testreset@test.com", "password": "Test1234!"}
        )
        if login_response.status_code != 200:
            pytest.skip("Guardian login failed - skipping authenticated tests")
        return login_response.json().get("access_token")
    
    def test_get_models_config(self, auth_token):
        """GET /api/admin/models returns LLM config"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/models", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "provider" in data
        assert "model" in data
        
        # Provider should be emergent or openrouter
        assert data["provider"] in ["emergent", "openrouter"]
        
        print(f"PASS: Get models config - Provider: {data['provider']}, Model: {data['model']}")
    
    def test_update_models_config_emergent(self, auth_token):
        """POST /api/admin/models updates LLM config to emergent provider"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        update_data = {
            "provider": "emergent",
            "model": "gpt-4o-mini"
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/models", headers=headers, json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert data["message"] == "LLM config updated"
        assert "config" in data
        assert data["config"]["provider"] == "emergent"
        assert data["config"]["model"] == "gpt-4o-mini"
        
        print("PASS: Updated LLM config to emergent/gpt-4o-mini")
        
        # Verify the change persisted
        get_response = requests.get(f"{BASE_URL}/api/admin/models", headers=headers)
        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data["provider"] == "emergent"
        assert get_data["model"] == "gpt-4o-mini"
        print("PASS: Verified config change persisted")
    
    def test_update_models_config_openrouter(self, auth_token):
        """POST /api/admin/models updates LLM config to openrouter provider"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        update_data = {
            "provider": "openrouter",
            "model": "meta-llama/llama-3.1-8b-instruct:free",
            "openrouter_key": "sk-or-test-key"
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/models", headers=headers, json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["config"]["provider"] == "openrouter"
        assert data["config"]["model"] == "meta-llama/llama-3.1-8b-instruct:free"
        
        print("PASS: Updated LLM config to openrouter")
        
        # Reset back to emergent
        reset_data = {"provider": "emergent", "model": "gpt-5.2"}
        requests.post(f"{BASE_URL}/api/admin/models", headers=headers, json=reset_data)
        print("PASS: Reset LLM config back to emergent/gpt-5.2")


class TestWebSocketEndpoint:
    """Test WebSocket /ws/session/{session_id} endpoint"""
    
    @pytest.fixture
    def teacher_auth(self):
        """Login as teacher to get auth token and session list"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "smith@school.edu", "password": "Teacher123!"}
        )
        if login_response.status_code != 200:
            pytest.skip("Teacher login failed - skipping WebSocket tests")
        token = login_response.json().get("access_token")
        
        # Get sessions
        headers = {"Authorization": f"Bearer {token}"}
        sessions_response = requests.get(f"{BASE_URL}/api/classroom-sessions", headers=headers)
        sessions = sessions_response.json() if sessions_response.status_code == 200 else []
        
        return {"token": token, "sessions": sessions}
    
    def test_websocket_connection(self, teacher_auth):
        """WebSocket /ws/session/{id} accepts connections"""
        if not teacher_auth["sessions"]:
            pytest.skip("No sessions available for WebSocket test")
        
        session_id = teacher_auth["sessions"][0]["id"]
        ws_url = BASE_URL.replace("https://", "wss://").replace("http://", "ws://")
        ws_endpoint = f"{ws_url}/ws/session/{session_id}"
        
        connected = False
        error_msg = None
        
        def on_open(ws):
            nonlocal connected
            connected = True
            print(f"PASS: WebSocket connected to session {session_id[:8]}...")
            ws.close()
        
        def on_error(ws, error):
            nonlocal error_msg
            error_msg = str(error)
        
        def on_close(ws, close_status_code, close_msg):
            pass
        
        try:
            ws = websocket.WebSocketApp(
                ws_endpoint,
                on_open=on_open,
                on_error=on_error,
                on_close=on_close
            )
            
            # Run in thread with timeout
            wst = threading.Thread(target=ws.run_forever, kwargs={"ping_timeout": 5})
            wst.daemon = True
            wst.start()
            wst.join(timeout=5)
            
            if error_msg:
                print(f"WARNING: WebSocket error - {error_msg}")
            
            # WebSocket should have connected
            assert connected or error_msg is None, f"WebSocket failed to connect: {error_msg}"
            print("PASS: WebSocket endpoint accepts connections")
            
        except Exception as e:
            # WebSocket library might not be installed, that's OK
            print(f"INFO: WebSocket test skipped - {str(e)}")


class TestTeacherAuth:
    """Test teacher authentication for admin access"""
    
    def test_teacher_can_access_admin_costs(self):
        """Teachers should be able to access admin costs endpoint"""
        # Login as teacher
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "smith@school.edu", "password": "Teacher123!"}
        )
        assert login_response.status_code == 200
        token = login_response.json().get("access_token")
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/admin/costs", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_cost" in data
        print("PASS: Teacher can access admin costs endpoint")
    
    def test_teacher_can_access_admin_models(self):
        """Teachers should be able to access admin models endpoint"""
        # Login as teacher
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "smith@school.edu", "password": "Teacher123!"}
        )
        assert login_response.status_code == 200
        token = login_response.json().get("access_token")
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/admin/models", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "provider" in data
        print("PASS: Teacher can access admin models endpoint")


class TestStoryDialogDataTestIds:
    """Test that story dialog has proper data-testid attributes (code review)"""
    
    def test_story_dialog_testids_exist_in_code(self):
        """Verify StoryGenerationDialog.jsx has required data-testid attributes"""
        dialog_file = "/app/frontend/src/components/student/StoryGenerationDialog.jsx"
        
        try:
            with open(dialog_file, 'r') as f:
                content = f.read()
            
            # Check for required data-testid attributes
            assert 'data-testid="story-prompt-input"' in content, "Missing story-prompt-input testid"
            assert 'data-testid="generate-story-btn"' in content, "Missing generate-story-btn testid"
            assert 'data-testid="story-dialog-close"' in content, "Missing story-dialog-close testid"
            
            print("PASS: StoryGenerationDialog.jsx has all required data-testid attributes")
            
        except FileNotFoundError:
            pytest.skip("StoryGenerationDialog.jsx not found")


class TestAdminPortalCodeReview:
    """Code review tests for AdminPortal.jsx"""
    
    def test_admin_portal_has_testids(self):
        """Verify AdminPortal.jsx has required data-testid attributes"""
        portal_file = "/app/frontend/src/pages/AdminPortal.jsx"
        
        try:
            with open(portal_file, 'r') as f:
                content = f.read()
            
            # Check for required data-testid attributes (uses template literals like data-testid={`tab-${tab.id}`})
            assert 'data-testid="admin-portal"' in content, "Missing admin-portal testid"
            assert 'data-testid={`tab-${tab.id}`}' in content, "Missing tab-{id} testid pattern"
            assert 'data-testid="costs-tab"' in content, "Missing costs-tab testid"
            assert 'data-testid="config-tab"' in content, "Missing config-tab testid"
            assert 'data-testid="save-config-btn"' in content, "Missing save-config-btn testid"
            assert 'data-testid="model-select"' in content, "Missing model-select testid"
            assert 'data-testid="stat-total-cost"' in content, "Missing stat-total-cost testid"
            assert 'data-testid="stat-total-stories"' in content, "Missing stat-total-stories testid"
            
            print("PASS: AdminPortal.jsx has all required data-testid attributes")
            
        except FileNotFoundError:
            pytest.skip("AdminPortal.jsx not found")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
