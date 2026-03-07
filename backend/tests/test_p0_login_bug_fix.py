"""
Test P0 Login Bug Fix - Iteration 17
Tests for Parent/School login flow that was previously broken due to NameError in server.py

Root cause: get_current_brand_partner function was defined at line 3513 but used at line 2498
Fix: Moved function definition before first usage

Test scenarios:
1. Guardian (Parent/School) login
2. Admin login
3. Registration followed by login
4. GET /api/students with valid token
5. Backend health check
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from main agent
GUARDIAN_EMAIL = "allen@ourfamily.contact"
GUARDIAN_PASSWORD = "LexiAdmin2026!"
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestBackendHealth:
    """Verify backend is running without NameError crash"""

    def test_health_endpoint(self, api_client):
        """Backend health check - should return 200, not 502"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Backend unhealthy: {response.text}"
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✓ Health check passed: {data}")


class TestGuardianLogin:
    """Test Parent/School (guardian) login - PRIMARY P0 bug fix verification"""

    def test_guardian_login_success(self, api_client):
        """P0 FIX: Guardian login should return 200 with access_token, not 502"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": GUARDIAN_EMAIL,
            "password": GUARDIAN_PASSWORD
        })
        # This was returning 502 due to NameError before fix
        assert response.status_code == 200, f"Guardian login failed: {response.status_code} - {response.text}"
        
        data = response.json()
        # Verify response structure
        assert "access_token" in data, "Missing access_token in response"
        assert "user" in data, "Missing user in response"
        assert data["user"]["role"] == "guardian", f"Expected guardian role, got {data['user']['role']}"
        assert data["user"]["email"] == GUARDIAN_EMAIL
        print(f"✓ Guardian login successful: {data['user']['email']} ({data['user']['role']})")
        return data

    def test_guardian_login_invalid_password(self, api_client):
        """Guardian login with wrong password returns 401, not 502"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": GUARDIAN_EMAIL,
            "password": "WrongPassword123"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid password correctly returns 401")


class TestAdminLogin:
    """Test Admin login"""

    def test_admin_login_success(self, api_client):
        """Admin login should return 200 with access_token"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "admin"
        print(f"✓ Admin login successful: {data['user']['email']} ({data['user']['role']})")
        return data


class TestRegistrationAndLogin:
    """Test registration followed by login - validates new user flow"""
    
    def test_register_guardian_and_login(self, api_client):
        """Register new guardian then login"""
        import time
        test_email = f"test_p0_{int(time.time())}@example.com"
        
        # Register
        register_response = api_client.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "full_name": "Test P0 User",
            "password": "TestPass123!",
            "role": "guardian"
        })
        assert register_response.status_code == 200, f"Registration failed: {register_response.text}"
        print(f"✓ Registration successful for {test_email}")
        
        # Login with new account
        login_response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_email,
            "password": "TestPass123!"
        })
        assert login_response.status_code == 200, f"Login failed after registration: {login_response.text}"
        
        data = login_response.json()
        assert data["user"]["email"] == test_email
        assert data["user"]["role"] == "guardian"
        print(f"✓ Login after registration successful")
        return data


class TestStudentsAPIWithToken:
    """Test authenticated API access - verifies token validation works"""

    def test_get_students_with_guardian_token(self, api_client):
        """GET /api/students with valid guardian token should return 200"""
        # First login to get token
        login_response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": GUARDIAN_EMAIL,
            "password": GUARDIAN_PASSWORD
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        guardian_id = login_response.json()["user"]["id"]
        
        # Get students with token
        api_client.headers.update({"Authorization": f"Bearer {token}"})
        students_response = api_client.get(f"{BASE_URL}/api/students?guardian_id={guardian_id}")
        
        # Should return 200 with array (empty or with students), not 401 or 502
        assert students_response.status_code == 200, f"Students API failed: {students_response.status_code} - {students_response.text}"
        data = students_response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✓ GET /api/students returned {len(data)} students")

    def test_get_students_without_token(self, api_client):
        """GET /api/students without token should return 401 or 403"""
        response = api_client.get(f"{BASE_URL}/api/students")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ Unauthenticated request correctly rejected with {response.status_code}")


class TestGetCurrentUser:
    """Test /api/auth/me endpoint - validates JWT decode works"""

    def test_get_me_with_guardian_token(self, api_client):
        """GET /api/auth/me should return current user info"""
        # Login first
        login_response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": GUARDIAN_EMAIL,
            "password": GUARDIAN_PASSWORD
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Get current user
        api_client.headers.update({"Authorization": f"Bearer {token}"})
        me_response = api_client.get(f"{BASE_URL}/api/auth/me")
        
        assert me_response.status_code == 200, f"GET /me failed: {me_response.text}"
        data = me_response.json()
        assert data["email"] == GUARDIAN_EMAIL
        print(f"✓ GET /api/auth/me returned: {data['email']}")


class TestLoginResponseFormat:
    """Verify login response contains all required fields"""

    def test_login_response_has_required_fields(self, api_client):
        """Login response should have access_token, token_type, and user object"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": GUARDIAN_EMAIL,
            "password": GUARDIAN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        
        # Required top-level fields
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        
        # Required user fields
        user = data["user"]
        assert "id" in user
        assert "email" in user
        assert "full_name" in user
        assert "role" in user
        assert "wallet_balance" in user
        assert "referral_code" in user
        
        print(f"✓ Login response format validated: {list(data.keys())}")
        print(f"✓ User fields: {list(user.keys())}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
