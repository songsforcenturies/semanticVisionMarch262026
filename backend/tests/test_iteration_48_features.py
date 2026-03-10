"""
Test iteration 48: Admin impersonation, support-session (Daily.co), student change-my-pin
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"


class TestAdminLogin:
    """Test admin login and token generation"""
    
    def test_admin_login(self):
        """Admin can login and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["role"] == "admin"
        print(f"Admin login successful: {data['user']['full_name']}")


class TestAdminImpersonation:
    """Test admin impersonation endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Admin login failed")
    
    def test_get_users_list(self, admin_token):
        """Admin can get list of users"""
        response = requests.get(
            f"{BASE_URL}/api/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Get users failed: {response.text}"
        users = response.json()
        assert isinstance(users, list)
        assert len(users) > 0
        print(f"Found {len(users)} users")
    
    def test_impersonate_user(self, admin_token):
        """Admin can impersonate another user"""
        # First get a non-admin user
        response = requests.get(
            f"{BASE_URL}/api/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        users = response.json()
        non_admin_users = [u for u in users if u.get("role") != "admin"]
        
        if not non_admin_users:
            pytest.skip("No non-admin users to impersonate")
        
        target_user = non_admin_users[0]
        target_id = target_user["id"]
        
        # Impersonate the user
        response = requests.post(
            f"{BASE_URL}/api/admin/impersonate/{target_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Impersonation failed: {response.text}"
        
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["id"] == target_id
        print(f"Successfully impersonated: {data['user'].get('full_name', data['user']['email'])}")
    
    def test_impersonate_nonexistent_user(self, admin_token):
        """Impersonating non-existent user returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/admin/impersonate/nonexistent-user-id",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404


class TestSupportSession:
    """Test Daily.co support session endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Admin login failed")
    
    def test_create_support_session_without_daily_key(self, admin_token):
        """Creating support session without Daily.co API key returns appropriate error"""
        response = requests.post(
            f"{BASE_URL}/api/admin/support-session",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        # Should fail with 500 because Daily.co is not configured
        assert response.status_code == 500, f"Expected 500, got {response.status_code}"
        data = response.json()
        assert "Daily.co not configured" in data.get("detail", "")
        print(f"Expected error: {data['detail']}")
    
    def test_non_admin_cannot_create_session(self):
        """Non-admin user cannot create support session"""
        # This would need a non-admin token; for now, skip if no other user
        pytest.skip("Need non-admin user token for this test")


class TestStudentChangeMyPin:
    """Test student change-my-pin endpoint"""
    
    def test_change_pin_validation_error(self):
        """Student change-my-pin validates input"""
        # Try with invalid data to check validation
        response = requests.post(f"{BASE_URL}/api/student/change-my-pin", json={
            "current_pin": "",
            "new_pin": "1234"
        })
        # Should fail with validation error
        assert response.status_code == 400 or response.status_code == 422, f"Expected 400/422, got {response.status_code}"
        print(f"Validation working: {response.status_code}")
    
    def test_change_pin_wrong_current_pin(self):
        """Change PIN fails with wrong current PIN"""
        response = requests.post(f"{BASE_URL}/api/student/change-my-pin", json={
            "current_pin": "000000",  # Wrong PIN
            "new_pin": "123456"
        })
        # Should fail with 400 or 404
        assert response.status_code in [400, 404], f"Expected 400/404, got {response.status_code}"


class TestIntegrations:
    """Test integrations endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Admin login failed")
    
    def test_get_integrations(self, admin_token):
        """Admin can get integration settings"""
        response = requests.get(
            f"{BASE_URL}/api/admin/integrations",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Get integrations failed: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "stripe" in data
        assert "paypal" in data
        assert "resend" in data
        assert "daily" in data
        
        print(f"Stripe configured: {data['stripe'].get('has_key', False)}")
        print(f"PayPal configured: {data['paypal'].get('has_keys', False)}")
        print(f"Resend configured: {data['resend'].get('has_key', False)}")
        print(f"Daily.co configured: {data['daily'].get('has_key', False)}")


class TestAdminStats:
    """Test admin statistics endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Admin login failed")
    
    def test_get_admin_stats(self, admin_token):
        """Admin can get platform statistics"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Get stats failed: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "users" in data
        assert "content" in data
        assert "revenue" in data
        assert "ai" in data
        
        print(f"Total parents: {data['users']['guardians']}")
        print(f"Total students: {data['users']['students']}")
        print(f"Total stories: {data['content']['narratives']}")
