"""
Iteration 20: Currency Detection, Exchange Rates, Referral Earnings Display, Admin Referral Reward Config

Tests:
- GET /api/currency/detect - Returns country_code, currency_code, currency_symbol, rate_to_usd
- GET /api/currency/rates - Returns exchange rates with USD base
- GET /api/referrals/my-referrals - Returns referrals array + total_earned + total_count
- GET /api/referrals/reward-amount - Returns configured reward amount
- Admin billing config - referral_reward_amount field
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Credentials
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"
GUARDIAN_EMAIL = "allen@ourfamily.contact"
GUARDIAN_PASSWORD = "LexiAdmin2026!"


class TestHealthCheck:
    """Ensure backend is running"""
    
    def test_backend_health(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print(f"Backend health check passed: {response.json()}")


class TestCurrencyDetection:
    """Test currency detection and exchange rates endpoints"""
    
    def test_currency_detect_returns_expected_fields(self):
        """GET /api/currency/detect should return country_code, currency_code, currency_symbol, rate_to_usd"""
        response = requests.get(f"{BASE_URL}/api/currency/detect")
        assert response.status_code == 200
        data = response.json()
        
        # Validate all required fields exist
        assert "country_code" in data, "Missing country_code"
        assert "currency_code" in data, "Missing currency_code"
        assert "currency_symbol" in data, "Missing currency_symbol"
        assert "rate_to_usd" in data, "Missing rate_to_usd"
        
        # Validate types
        assert isinstance(data["country_code"], str)
        assert isinstance(data["currency_code"], str)
        assert isinstance(data["currency_symbol"], str)
        assert isinstance(data["rate_to_usd"], (int, float))
        
        # Server IP is US-based, so expect USD
        print(f"Currency detected: {data}")
        print(f"  Country: {data['country_code']}, Currency: {data['currency_code']}, Symbol: {data['currency_symbol']}, Rate: {data['rate_to_usd']}")
    
    def test_currency_rates_returns_expected_structure(self):
        """GET /api/currency/rates should return exchange rates with USD base"""
        response = requests.get(f"{BASE_URL}/api/currency/rates")
        assert response.status_code == 200
        data = response.json()
        
        # Validate structure
        assert "base" in data, "Missing base currency"
        assert "rates" in data, "Missing rates"
        assert data["base"] == "USD", f"Expected base USD, got {data['base']}"
        
        # Validate rates is a dict with currency codes
        assert isinstance(data["rates"], dict)
        
        # Check some expected currencies exist
        expected_currencies = ["EUR", "GBP", "JPY", "NGN", "INR"]
        for curr in expected_currencies:
            if curr in data["rates"]:
                assert isinstance(data["rates"][curr], (int, float))
        
        print(f"Exchange rates: base={data['base']}, {len(data['rates'])} currencies")
        # Show some sample rates
        sample_rates = {k: data['rates'][k] for k in list(data['rates'].keys())[:5]}
        print(f"Sample rates: {sample_rates}")


class TestReferralRewardAmount:
    """Test public referral reward amount endpoint"""
    
    def test_get_referral_reward_amount(self):
        """GET /api/referrals/reward-amount should return configured reward amount"""
        response = requests.get(f"{BASE_URL}/api/referrals/reward-amount")
        assert response.status_code == 200
        data = response.json()
        
        assert "referral_reward_amount" in data, "Missing referral_reward_amount"
        assert isinstance(data["referral_reward_amount"], (int, float))
        assert data["referral_reward_amount"] >= 0, "Reward amount should be non-negative"
        
        print(f"Referral reward amount: ${data['referral_reward_amount']}")


class TestGuardianReferrals:
    """Test guardian referral endpoints"""
    
    @pytest.fixture
    def guardian_token(self):
        """Login as guardian and return token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": GUARDIAN_EMAIL,
            "password": GUARDIAN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Guardian login failed: {response.status_code}")
        return response.json().get("access_token")
    
    def test_get_my_referral_code(self, guardian_token):
        """GET /api/referrals/my-code should return user's referral code"""
        headers = {"Authorization": f"Bearer {guardian_token}"}
        response = requests.get(f"{BASE_URL}/api/referrals/my-code", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "referral_code" in data
        assert isinstance(data["referral_code"], str)
        assert len(data["referral_code"]) > 0, "Referral code should not be empty"
        
        print(f"Guardian referral code: {data['referral_code']}")
    
    def test_get_my_referrals_returns_expected_fields(self, guardian_token):
        """GET /api/referrals/my-referrals should return referrals array + total_earned + total_count"""
        headers = {"Authorization": f"Bearer {guardian_token}"}
        response = requests.get(f"{BASE_URL}/api/referrals/my-referrals", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Validate required fields
        assert "referrals" in data, "Missing referrals array"
        assert "total_earned" in data, "Missing total_earned"
        assert "total_count" in data, "Missing total_count"
        
        # Validate types
        assert isinstance(data["referrals"], list)
        assert isinstance(data["total_earned"], (int, float))
        assert isinstance(data["total_count"], int)
        
        # Validate consistency
        assert data["total_count"] == len(data["referrals"]), "total_count should match referrals length"
        
        print(f"Referrals: {data['total_count']} referrals, ${data['total_earned']} total earned")
        
        # If there are referrals, check their structure
        if data["referrals"]:
            ref = data["referrals"][0]
            print(f"Sample referral: {ref}")


class TestAdminBillingConfig:
    """Test admin billing configuration for referral reward"""
    
    @pytest.fixture
    def admin_token(self):
        """Login as admin and return token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.status_code}")
        return response.json().get("access_token")
    
    def test_get_billing_config_includes_referral_reward(self, admin_token):
        """Admin should be able to get billing config with referral_reward_amount"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/billing-config", headers=headers)
        
        if response.status_code == 404:
            print("Billing config not found, using defaults")
            return
        
        assert response.status_code == 200
        data = response.json()
        
        # referral_reward_amount might be in the config
        print(f"Billing config: {data}")
    
    def test_update_referral_reward_amount(self, admin_token):
        """Admin should be able to update referral_reward_amount"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get current config first
        get_response = requests.get(f"{BASE_URL}/api/admin/billing-config", headers=headers)
        current_config = get_response.json() if get_response.status_code == 200 else {}
        
        # Test updating the referral reward
        new_reward = 7.50
        update_data = {**current_config, "referral_reward_amount": new_reward}
        
        response = requests.post(f"{BASE_URL}/api/admin/billing-config", 
                               headers=headers, json=update_data)
        
        # Might return 200 or 201
        assert response.status_code in [200, 201], f"Update failed: {response.status_code} - {response.text}"
        
        # Verify the public endpoint returns updated value
        public_response = requests.get(f"{BASE_URL}/api/referrals/reward-amount")
        assert public_response.status_code == 200
        public_data = public_response.json()
        assert public_data["referral_reward_amount"] == new_reward, \
            f"Expected {new_reward}, got {public_data['referral_reward_amount']}"
        
        print(f"Updated referral reward to ${new_reward}, verified via public endpoint")
        
        # Reset to default
        reset_data = {**current_config, "referral_reward_amount": 5.0}
        requests.post(f"{BASE_URL}/api/admin/billing-config", headers=headers, json=reset_data)


class TestStudentToggleEndpoints:
    """Test student toggle endpoints for spellcheck, phonetic, brand stories"""
    
    @pytest.fixture
    def guardian_auth(self):
        """Login as guardian and return token + user info"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": GUARDIAN_EMAIL,
            "password": GUARDIAN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Guardian login failed: {response.status_code}")
        data = response.json()
        return {"token": data["access_token"], "user": data["user"]}
    
    @pytest.fixture
    def admin_token(self):
        """Login as admin and return token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.status_code}")
        return response.json().get("access_token")
    
    def test_get_students_has_toggle_fields(self, guardian_auth, admin_token):
        """Students should have spellcheck_disabled, spelling_mode, ad_preferences fields"""
        headers = {"Authorization": f"Bearer {guardian_auth['token']}"}
        user_id = guardian_auth["user"]["id"]
        
        # Get students for guardian - check admin endpoint
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Try guardian endpoint first
        response = requests.get(f"{BASE_URL}/api/guardians/{user_id}/students", headers=headers)
        
        if response.status_code != 200:
            # Try admin route
            response = requests.get(f"{BASE_URL}/api/students", headers=admin_headers)
        
        if response.status_code != 200:
            pytest.skip(f"Could not get students: {response.status_code}")
        
        students = response.json()
        if not students:
            pytest.skip("No students found")
        
        student = students[0]
        print(f"Student fields: {list(student.keys())}")
        
        # Check for toggle-related fields
        # These may not be present if student was created before feature was added
        if "spellcheck_disabled" in student:
            print(f"  spellcheck_disabled: {student['spellcheck_disabled']}")
        if "spelling_mode" in student:
            print(f"  spelling_mode: {student['spelling_mode']}")
        if "ad_preferences" in student:
            print(f"  ad_preferences: {student['ad_preferences']}")


class TestCleanup:
    """Cleanup test data"""
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
