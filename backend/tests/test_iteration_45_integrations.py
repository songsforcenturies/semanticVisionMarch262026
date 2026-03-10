"""
Iteration 45: Admin Integration Settings Panel Testing
Tests for GET/PUT /api/admin/integrations endpoints and PayPal config endpoint.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Admin credentials
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"

@pytest.fixture(scope="module")
def admin_token():
    """Get admin auth token"""
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    token = resp.json().get("access_token")
    assert token, "No access_token in login response"
    return token

@pytest.fixture(scope="module")
def admin_headers(admin_token):
    """Auth headers for admin requests"""
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


class TestIntegrationsEndpoint:
    """Tests for GET /api/admin/integrations"""
    
    def test_get_integrations_success(self, admin_headers):
        """GET /api/admin/integrations - returns masked keys with status"""
        resp = requests.get(f"{BASE_URL}/api/admin/integrations", headers=admin_headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        
        # Verify Stripe section
        assert "stripe" in data, "Response must contain 'stripe' section"
        stripe = data["stripe"]
        assert "api_key_masked" in stripe, "Stripe must have api_key_masked"
        assert "has_key" in stripe, "Stripe must have has_key boolean"
        assert "enabled" in stripe, "Stripe must have enabled boolean"
        assert stripe["has_key"] == True, "Stripe should have key configured (from .env)"
        
        # Verify PayPal section
        assert "paypal" in data, "Response must contain 'paypal' section"
        paypal = data["paypal"]
        assert "client_id_masked" in paypal, "PayPal must have client_id_masked"
        assert "secret_masked" in paypal, "PayPal must have secret_masked"
        assert "has_keys" in paypal, "PayPal must have has_keys boolean"
        assert "enabled" in paypal, "PayPal must have enabled boolean"
        assert "mode" in paypal, "PayPal must have mode (sandbox/live)"
        assert paypal["has_keys"] == False, "PayPal should NOT have keys (not configured in .env)"
        
        # Verify Resend section
        assert "resend" in data, "Response must contain 'resend' section"
        resend = data["resend"]
        assert "api_key_masked" in resend, "Resend must have api_key_masked"
        assert "has_key" in resend, "Resend must have has_key boolean"
        assert "enabled" in resend, "Resend must have enabled boolean"
        assert "sender_email" in resend, "Resend must have sender_email"
        assert resend["has_key"] == True, "Resend should have key configured (from .env)"
        
        print(f"✓ GET /api/admin/integrations - Stripe has_key: {stripe['has_key']}, PayPal has_keys: {paypal['has_keys']}, Resend has_key: {resend['has_key']}")
    
    def test_get_integrations_forbidden_for_non_admin(self, admin_token):
        """GET /api/admin/integrations - should return 401 or 403 for non-admin"""
        # Test without auth header - should fail
        resp = requests.get(f"{BASE_URL}/api/admin/integrations")
        assert resp.status_code in [401, 403], f"Expected 401/403 for unauthenticated, got {resp.status_code}"
        print(f"✓ GET /api/admin/integrations - Returns {resp.status_code} for unauthenticated user")
    
    def test_integrations_keys_are_masked(self, admin_headers):
        """Verify that returned keys are properly masked"""
        resp = requests.get(f"{BASE_URL}/api/admin/integrations", headers=admin_headers)
        assert resp.status_code == 200
        
        data = resp.json()
        
        # Stripe key should be masked (starts with * if key exists)
        if data["stripe"]["has_key"]:
            assert data["stripe"]["api_key_masked"].startswith("*"), "Stripe key should be masked"
            print(f"✓ Stripe key masked: {data['stripe']['api_key_masked']}")
        
        # Resend key should be masked
        if data["resend"]["has_key"]:
            assert data["resend"]["api_key_masked"].startswith("*"), "Resend key should be masked"
            print(f"✓ Resend key masked: {data['resend']['api_key_masked']}")


class TestUpdateIntegrations:
    """Tests for PUT /api/admin/integrations"""
    
    def test_update_integrations_sender_email(self, admin_headers):
        """PUT /api/admin/integrations - update sender_email"""
        # Get current settings first
        get_resp = requests.get(f"{BASE_URL}/api/admin/integrations", headers=admin_headers)
        assert get_resp.status_code == 200
        current = get_resp.json()
        
        # Update with new sender email
        test_sender_email = "Test Sender <test@semanticvision.ai>"
        update_data = {
            "stripe_api_key": current["stripe"]["api_key_masked"],
            "paypal_client_id": current["paypal"]["client_id_masked"],
            "paypal_secret": current["paypal"]["secret_masked"],
            "resend_api_key": current["resend"]["api_key_masked"],
            "sender_email": test_sender_email,
            "paypal_mode": current["paypal"]["mode"],
            "stripe_enabled": current["stripe"]["enabled"],
            "paypal_enabled": current["paypal"]["enabled"],
            "resend_enabled": current["resend"]["enabled"],
        }
        
        put_resp = requests.put(f"{BASE_URL}/api/admin/integrations", json=update_data, headers=admin_headers)
        assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"
        assert "message" in put_resp.json(), "Response should contain success message"
        
        print("✓ PUT /api/admin/integrations - Updated sender_email successfully")
        
        # Verify the change persisted
        verify_resp = requests.get(f"{BASE_URL}/api/admin/integrations", headers=admin_headers)
        assert verify_resp.status_code == 200
        verify_data = verify_resp.json()
        assert verify_data["resend"]["sender_email"] == test_sender_email, "sender_email should be updated"
        
        print(f"✓ Verified sender_email updated to: {verify_data['resend']['sender_email']}")
        
        # Restore original sender email
        update_data["sender_email"] = "Semantic Vision <hello@semanticvision.ai>"
        restore_resp = requests.put(f"{BASE_URL}/api/admin/integrations", json=update_data, headers=admin_headers)
        assert restore_resp.status_code == 200
        print("✓ Restored original sender_email")
    
    def test_update_integrations_toggle_paypal_enabled(self, admin_headers):
        """PUT /api/admin/integrations - toggle paypal_enabled"""
        # Get current settings
        get_resp = requests.get(f"{BASE_URL}/api/admin/integrations", headers=admin_headers)
        assert get_resp.status_code == 200
        current = get_resp.json()
        
        original_paypal_enabled = current["paypal"]["enabled"]
        
        # Toggle paypal_enabled to the opposite
        update_data = {
            "stripe_api_key": current["stripe"]["api_key_masked"],
            "paypal_client_id": current["paypal"]["client_id_masked"],
            "paypal_secret": current["paypal"]["secret_masked"],
            "resend_api_key": current["resend"]["api_key_masked"],
            "sender_email": current["resend"]["sender_email"],
            "paypal_mode": current["paypal"]["mode"],
            "stripe_enabled": current["stripe"]["enabled"],
            "paypal_enabled": not original_paypal_enabled,  # Toggle
            "resend_enabled": current["resend"]["enabled"],
        }
        
        put_resp = requests.put(f"{BASE_URL}/api/admin/integrations", json=update_data, headers=admin_headers)
        assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"
        
        # Verify change
        verify_resp = requests.get(f"{BASE_URL}/api/admin/integrations", headers=admin_headers)
        verify_data = verify_resp.json()
        assert verify_data["paypal"]["enabled"] == (not original_paypal_enabled), "paypal_enabled should be toggled"
        
        print(f"✓ paypal_enabled toggled from {original_paypal_enabled} to {verify_data['paypal']['enabled']}")
        
        # Restore original state
        update_data["paypal_enabled"] = original_paypal_enabled
        restore_resp = requests.put(f"{BASE_URL}/api/admin/integrations", json=update_data, headers=admin_headers)
        assert restore_resp.status_code == 200
        print("✓ Restored original paypal_enabled state")
    
    def test_update_integrations_forbidden_for_non_admin(self):
        """PUT /api/admin/integrations - should return 401/403 for unauthorized"""
        update_data = {"sender_email": "test@test.com"}
        resp = requests.put(f"{BASE_URL}/api/admin/integrations", json=update_data)
        assert resp.status_code in [401, 403], f"Expected 401/403 for unauthenticated, got {resp.status_code}"
        print("✓ PUT /api/admin/integrations - Returns 401/403 for unauthenticated user")


class TestPayPalConfigReflectsDB:
    """Tests for GET /api/paypal/config reflecting DB-stored settings"""
    
    def test_paypal_config_endpoint(self, admin_headers):
        """GET /api/paypal/config - should reflect DB-stored settings"""
        # Get integrations settings first
        int_resp = requests.get(f"{BASE_URL}/api/admin/integrations", headers=admin_headers)
        assert int_resp.status_code == 200
        int_data = int_resp.json()
        
        # Get PayPal config (public endpoint)
        config_resp = requests.get(f"{BASE_URL}/api/paypal/config")
        assert config_resp.status_code == 200, f"Expected 200, got {config_resp.status_code}"
        
        config = config_resp.json()
        assert "client_id" in config, "PayPal config should contain client_id"
        assert "enabled" in config, "PayPal config should contain enabled"
        
        # PayPal should be disabled when no keys are configured
        if not int_data["paypal"]["has_keys"]:
            assert config["enabled"] == False, "PayPal should be disabled when no keys configured"
            print("✓ GET /api/paypal/config - PayPal correctly disabled (no keys)")
        else:
            print(f"✓ GET /api/paypal/config - PayPal enabled: {config['enabled']}")


class TestHealthAndBasicEndpoints:
    """Basic health check tests"""
    
    def test_health_endpoint(self):
        """GET /api/health - should return healthy"""
        resp = requests.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        print("✓ GET /api/health - Backend is healthy")
    
    def test_admin_login(self):
        """POST /api/auth/login - admin should login successfully"""
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        assert resp.status_code == 200, f"Login failed: {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "access_token" in data, "Login response must contain access_token"
        print("✓ POST /api/auth/login - Admin login successful")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
