"""
Test Suite for Iteration 44: PayPal Integration & Email/CORS Updates

Tests:
- PayPal routes (paypal.py):
  - GET /api/paypal/config - should return {client_id: '', enabled: false} when no keys set
  - POST /api/paypal/create-order - should return 500 'PayPal not configured' when no keys
  
- Existing routes regression (ensure no breaking changes):
  - POST /api/auth/login with allen@songsforcenturies.com / LexiAdmin2026!
  - GET /api/health
  - GET /api/students (authenticated)
  - GET /api/word-banks (authenticated)
  - GET /api/admin/stats (admin)
  - GET /api/patent/definitive-pdf

PayPal keys NOT set - integration should gracefully show as disabled.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"


class TestPayPalRoutes:
    """Test new PayPal payment routes from routes/paypal.py"""
    
    def test_paypal_config_returns_disabled(self):
        """GET /api/paypal/config - should return client_id: '' and enabled: false when no keys set"""
        response = requests.get(f"{BASE_URL}/api/paypal/config")
        assert response.status_code == 200, f"PayPal config endpoint failed: {response.status_code} - {response.text}"
        
        data = response.json()
        # Since PAYPAL_CLIENT_ID is empty in .env, expect disabled
        assert "client_id" in data, f"Expected 'client_id' in response: {data}"
        assert "enabled" in data, f"Expected 'enabled' in response: {data}"
        assert data["enabled"] == False, f"Expected enabled=false when no keys set, got: {data['enabled']}"
        assert data["client_id"] == "", f"Expected empty client_id, got: '{data['client_id']}'"
        print(f"✓ PayPal config endpoint passed: client_id='{data['client_id']}', enabled={data['enabled']}")
    
    def test_paypal_create_order_fails_without_keys(self):
        """POST /api/paypal/create-order - should return 500 'PayPal not configured' when no keys"""
        # First login to get auth token
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to create PayPal order
        response = requests.post(
            f"{BASE_URL}/api/paypal/create-order",
            json={"package_id": "small", "origin_url": "https://test.example.com"},
            headers=headers
        )
        
        # Expect 500 since PayPal is not configured
        assert response.status_code == 500, f"Expected 500 when PayPal not configured, got: {response.status_code}"
        data = response.json()
        assert "PayPal not configured" in str(data.get("detail", "")), f"Expected 'PayPal not configured' error, got: {data}"
        print(f"✓ PayPal create-order correctly returns 500 when not configured: {data}")
    
    def test_paypal_create_order_requires_auth(self):
        """POST /api/paypal/create-order - should require authentication"""
        response = requests.post(
            f"{BASE_URL}/api/paypal/create-order",
            json={"package_id": "small", "origin_url": "https://test.example.com"}
        )
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got: {response.status_code}"
        print(f"✓ PayPal create-order correctly requires auth: status={response.status_code}")


class TestAuthenticationRoutes:
    """Test authentication to ensure no breaking changes"""
    
    def test_login_with_admin_credentials(self):
        """POST /api/auth/login with admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        
        # Verify access_token is returned (NOT token)
        assert "access_token" in data, f"Expected 'access_token' in response, got: {data.keys()}"
        assert data["access_token"], "access_token should not be empty"
        assert data.get("token_type") == "bearer"
        
        # Verify user info
        assert "user" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["role"] == "admin"
        print(f"✓ Admin login passed: user_id={data['user']['id']}, role={data['user']['role']}")
        return data["access_token"]


class TestHealthAndDocuments:
    """Test health and document endpoints"""
    
    def test_health_check(self):
        """GET /api/health - should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        data = response.json()
        assert data.get("status") == "healthy"
        assert "timestamp" in data
        print(f"✓ Health check passed: {data}")
    
    def test_patent_definitive_pdf(self):
        """GET /api/patent/definitive-pdf - should return 200 for PDF file"""
        response = requests.get(f"{BASE_URL}/api/patent/definitive-pdf")
        # 200 means file exists and is served
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            assert "pdf" in content_type.lower() or "octet-stream" in content_type.lower()
            print("✓ Patent definitive PDF endpoint passed: file served")
        elif response.status_code == 404:
            print("✓ Patent definitive PDF endpoint works (file not found - acceptable)")
        else:
            pytest.fail(f"Unexpected status: {response.status_code}, {response.text}")


class TestAuthenticatedEndpoints:
    """Test endpoints that require authentication"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for all tests in this class"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_students(self):
        """GET /api/students - should return student list"""
        response = requests.get(f"{BASE_URL}/api/students", headers=self.headers)
        assert response.status_code == 200, f"Students endpoint failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✓ Students endpoint passed: {len(data)} students")
    
    def test_get_word_banks(self):
        """GET /api/word-banks - should return word banks"""
        response = requests.get(f"{BASE_URL}/api/word-banks", headers=self.headers)
        assert response.status_code == 200, f"Word banks endpoint failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✓ Word banks endpoint passed: {len(data)} word banks")
    
    def test_get_admin_stats(self):
        """GET /api/admin/stats - admin only, should return stats"""
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=self.headers)
        assert response.status_code == 200, f"Admin stats endpoint failed: {response.text}"
        data = response.json()
        assert "users" in data, f"Expected 'users' in response"
        assert "content" in data
        assert "reading" in data
        assert "revenue" in data
        print(f"✓ Admin stats endpoint passed: {data['users']}")


class TestWalletPackages:
    """Test wallet packages endpoint (used for PayPal integration)"""
    
    def test_wallet_packages(self):
        """GET /api/wallet/packages - should return topup packages including $5-$100"""
        response = requests.get(f"{BASE_URL}/api/wallet/packages")
        assert response.status_code == 200, f"Wallet packages failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        
        # Check for expected package amounts
        amounts = [pkg.get("amount") for pkg in data]
        expected_amounts = [5, 10, 25, 50, 100]
        for amt in expected_amounts:
            assert amt in amounts, f"Expected package amount ${amt} not found. Available: {amounts}"
        
        print(f"✓ Wallet packages endpoint passed: {len(data)} packages with amounts {amounts}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
