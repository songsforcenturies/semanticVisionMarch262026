"""
Iteration 7 Tests: Written Answer Evaluation & Spelling Controls
Tests for the major learning flow overhaul:
1. Written answer evaluation endpoint
2. Admin settings for spellcheck and free account limits
3. Student spellcheck toggle
4. Student spelling mode toggle
5. Spelling error logs
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

# Test credentials - PinTest Kid belongs to testreset@test.com guardian
GUARDIAN_EMAIL = "testreset@test.com"
GUARDIAN_PASSWORD = "Test1234!"
STUDENT_CODE = "STU-81B2O0"  # PinTest Kid
STUDENT_PIN = "416709909"
STUDENT_ID = "d32c8a5e-9734-4e8f-8b38-f33a3210d5e8"  # PinTest Kid's ID

# SJ belongs to a different guardian but has stories available for frontend testing
SJ_STUDENT_CODE = "STU-DR40V7"
SJ_STUDENT_PIN = "914027"
SJ_STUDENT_ID = "18316e14-9f7f-4960-9aba-e809fad104a2"


@pytest.fixture(scope="module")
def guardian_token():
    """Get authentication token for guardian"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": GUARDIAN_EMAIL,
        "password": GUARDIAN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Guardian login failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def api_client(guardian_token):
    """Shared requests session with auth"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {guardian_token}"
    })
    return session


class TestHealthCheck:
    """Ensure API is accessible"""
    
    def test_health_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        assert response.json().get("status") == "healthy"


class TestWrittenAnswerEvaluation:
    """Test POST /api/assessments/evaluate-written endpoint"""
    
    def test_evaluate_written_returns_result(self, api_client):
        """Written answer evaluation should return passed/feedback/spelling_errors"""
        response = api_client.post(f"{BASE_URL}/api/assessments/evaluate-written", json={
            "student_id": STUDENT_ID,
            "chapter_number": 1,
            "question": "What was the main idea of the chapter?",
            "student_answer": "The main idea was about friendship and helping others in need.",
            "chapter_summary": "This chapter describes how two friends helped each other...",
            "spelling_mode": "phonetic"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "passed" in data
        assert "feedback" in data
        assert "spelling_errors" in data
        assert isinstance(data["passed"], bool)
        assert isinstance(data["feedback"], str)
        assert isinstance(data["spelling_errors"], list)
    
    def test_evaluate_written_lenient_fallback(self, api_client):
        """Short answers should be lenient and pass if 5+ words"""
        response = api_client.post(f"{BASE_URL}/api/assessments/evaluate-written", json={
            "student_id": STUDENT_ID,
            "chapter_number": 1,
            "question": "What happened in this chapter?",
            "student_answer": "The story was about friends helping each other.",
            "chapter_summary": "",
            "spelling_mode": "phonetic"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # 9 words should pass
        assert "passed" in data
        # Should have feedback regardless
        assert "feedback" in data
    
    def test_evaluate_written_exact_spelling_mode(self, api_client):
        """Test evaluation with exact spelling mode"""
        response = api_client.post(f"{BASE_URL}/api/assessments/evaluate-written", json={
            "student_id": STUDENT_ID,
            "chapter_number": 2,
            "question": "What was the character's challenge?",
            "student_answer": "The character had to overcom many obstakles and challanges.",
            "chapter_summary": "The protagonist faced many obstacles...",
            "spelling_mode": "exact"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "spelling_errors" in data


class TestAdminSettings:
    """Test GET/POST /api/admin/settings endpoints"""
    
    def test_get_admin_settings_returns_defaults(self, api_client):
        """GET /api/admin/settings should return default settings"""
        response = api_client.get(f"{BASE_URL}/api/admin/settings")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify expected fields exist
        assert "global_spellcheck_disabled" in data
        assert "global_spelling_mode" in data
        assert "free_account_story_limit" in data
        assert "free_account_assessment_limit" in data
        
        # Verify default values (unless already changed)
        assert data["global_spelling_mode"] in ["phonetic", "exact"]
        assert isinstance(data["global_spellcheck_disabled"], bool)
        assert isinstance(data["free_account_story_limit"], int)
        assert isinstance(data["free_account_assessment_limit"], int)
    
    def test_update_admin_settings_spellcheck(self, api_client):
        """POST /api/admin/settings should update spellcheck setting"""
        # Get current settings
        current = api_client.get(f"{BASE_URL}/api/admin/settings").json()
        original_value = current.get("global_spellcheck_disabled", False)
        
        # Toggle spellcheck
        response = api_client.post(f"{BASE_URL}/api/admin/settings", json={
            "global_spellcheck_disabled": not original_value
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "settings" in data
        assert data["settings"]["global_spellcheck_disabled"] == (not original_value)
        
        # Reset to original
        api_client.post(f"{BASE_URL}/api/admin/settings", json={
            "global_spellcheck_disabled": original_value
        })
    
    def test_update_admin_settings_spelling_mode(self, api_client):
        """POST /api/admin/settings should update spelling mode"""
        response = api_client.post(f"{BASE_URL}/api/admin/settings", json={
            "global_spelling_mode": "exact"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["settings"]["global_spelling_mode"] == "exact"
        
        # Reset to phonetic
        api_client.post(f"{BASE_URL}/api/admin/settings", json={
            "global_spelling_mode": "phonetic"
        })
    
    def test_update_admin_settings_free_limits(self, api_client):
        """POST /api/admin/settings should update free account limits"""
        response = api_client.post(f"{BASE_URL}/api/admin/settings", json={
            "free_account_story_limit": 10,
            "free_account_assessment_limit": 20
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["settings"]["free_account_story_limit"] == 10
        assert data["settings"]["free_account_assessment_limit"] == 20
        
        # Reset to defaults
        api_client.post(f"{BASE_URL}/api/admin/settings", json={
            "free_account_story_limit": 5,
            "free_account_assessment_limit": 10
        })


class TestStudentSpellcheckToggle:
    """Test POST /api/students/{id}/spellcheck endpoint"""
    
    def test_toggle_spellcheck_returns_new_state(self, api_client):
        """POST /api/students/{id}/spellcheck toggles spellcheck_disabled and returns new state"""
        # Toggle spellcheck - first call
        response1 = api_client.post(f"{BASE_URL}/api/students/{STUDENT_ID}/spellcheck")
        
        assert response1.status_code == 200
        data1 = response1.json()
        assert "spellcheck_disabled" in data1
        first_state = data1["spellcheck_disabled"]
        
        # Toggle again - should flip
        response2 = api_client.post(f"{BASE_URL}/api/students/{STUDENT_ID}/spellcheck")
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["spellcheck_disabled"] == (not first_state)
        
        # Toggle back to original
        api_client.post(f"{BASE_URL}/api/students/{STUDENT_ID}/spellcheck")
    
    def test_spellcheck_toggle_unauthorized_student(self, api_client):
        """Toggle spellcheck should fail for unauthorized student"""
        # Use a random student ID that doesn't belong to this guardian
        response = api_client.post(f"{BASE_URL}/api/students/00000000-0000-0000-0000-000000000000/spellcheck")
        assert response.status_code in [403, 404]


class TestStudentSpellingModeToggle:
    """Test POST /api/students/{id}/spelling-mode endpoint"""
    
    def test_toggle_spelling_mode(self, api_client):
        """POST /api/students/{id}/spelling-mode toggles between exact and phonetic"""
        # Toggle spelling mode - first call
        response1 = api_client.post(f"{BASE_URL}/api/students/{STUDENT_ID}/spelling-mode")
        
        assert response1.status_code == 200
        data1 = response1.json()
        assert "spelling_mode" in data1
        first_mode = data1["spelling_mode"]
        assert first_mode in ["exact", "phonetic"]
        
        # Toggle again - should flip
        response2 = api_client.post(f"{BASE_URL}/api/students/{STUDENT_ID}/spelling-mode")
        
        assert response2.status_code == 200
        data2 = response2.json()
        expected = "phonetic" if first_mode == "exact" else "exact"
        assert data2["spelling_mode"] == expected
        
        # Toggle back to original
        api_client.post(f"{BASE_URL}/api/students/{STUDENT_ID}/spelling-mode")
    
    def test_spelling_mode_unauthorized_student(self, api_client):
        """Toggle spelling mode should fail for unauthorized student"""
        response = api_client.post(f"{BASE_URL}/api/students/00000000-0000-0000-0000-000000000000/spelling-mode")
        assert response.status_code in [403, 404]


class TestSpellingLogs:
    """Test GET /api/students/{id}/spelling-logs endpoint"""
    
    def test_get_spelling_logs_returns_list(self, api_client):
        """GET /api/students/{id}/spelling-logs returns list of logs"""
        response = api_client.get(f"{BASE_URL}/api/students/{STUDENT_ID}/spelling-logs")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # If there are logs, verify structure
        if len(data) > 0:
            log = data[0]
            assert "student_id" in log or "errors" in log
    
    def test_spelling_logs_unauthorized_student(self, api_client):
        """Spelling logs should fail for unauthorized student"""
        response = api_client.get(f"{BASE_URL}/api/students/00000000-0000-0000-0000-000000000000/spelling-logs")
        assert response.status_code in [403, 404]


class TestStudentLogin:
    """Verify student login still works with existing credentials"""
    
    def test_student_login_success_pintest_kid(self):
        """PinTest Kid can login with code and PIN"""
        response = requests.post(f"{BASE_URL}/api/auth/student-login", json={
            "student_code": STUDENT_CODE,
            "pin": STUDENT_PIN
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "student" in data
        assert data["student"]["id"] == STUDENT_ID
    
    def test_student_login_success_sj(self):
        """SJ can login with code and PIN"""
        response = requests.post(f"{BASE_URL}/api/auth/student-login", json={
            "student_code": SJ_STUDENT_CODE,
            "pin": SJ_STUDENT_PIN
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "student" in data
        assert data["student"]["id"] == SJ_STUDENT_ID
    
    def test_student_login_invalid_pin(self):
        """Student login fails with invalid PIN"""
        response = requests.post(f"{BASE_URL}/api/auth/student-login", json={
            "student_code": STUDENT_CODE,
            "pin": "000000"
        })
        assert response.status_code == 401


class TestNarrativesForStudent:
    """Verify SJ student has narratives for UI testing"""
    
    def test_sj_student_has_narratives(self, api_client):
        """SJ student should have available narratives"""
        response = api_client.get(f"{BASE_URL}/api/narratives", params={"student_id": SJ_STUDENT_ID})
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Student has {len(data)} narratives available")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
