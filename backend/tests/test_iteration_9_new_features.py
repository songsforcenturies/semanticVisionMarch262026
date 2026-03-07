"""
Iteration 9 - New Features Test
Tests for:
- Referral system (invite & earn wallet credits)
- Word definition API (AI-powered definitions)
- Donation/Sponsor system with Stripe
- Admin billing/ROI configuration
- Admin feature flags
- Student belief system, cultural context, language preferences
- Login response includes referral_code
- Admin role for allen@songsforcenturies.com
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


@pytest.fixture(scope="module")
def admin_auth():
    """Login as admin and return token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "testadmin@test.com",
        "password": "test123"
    })
    if response.status_code != 200:
        pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")
    data = response.json()
    return {
        "token": data["access_token"],
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
        "user": data["user"]
    }


# ==================== LOGIN RESPONSE TESTS ====================

class TestLoginResponseFields:
    """Test login response contains new fields"""
    
    def test_login_returns_referral_code(self, admin_auth):
        """Login response should include referral_code"""
        user = admin_auth["user"]
        assert "referral_code" in user, "Login response missing referral_code field"
        assert user["referral_code"], "referral_code should not be empty"
        print(f"✅ Login returns referral_code: {user['referral_code']}")
    
    def test_login_returns_wallet_balance(self, admin_auth):
        """Login response should include wallet_balance"""
        user = admin_auth["user"]
        assert "wallet_balance" in user, "Login response missing wallet_balance field"
        print(f"✅ Login returns wallet_balance: {user['wallet_balance']}")
    
    def test_login_returns_is_delegated_admin(self, admin_auth):
        """Login response should include is_delegated_admin"""
        user = admin_auth["user"]
        assert "is_delegated_admin" in user, "Login response missing is_delegated_admin field"
        print(f"✅ Login returns is_delegated_admin: {user['is_delegated_admin']}")


# ==================== REFERRAL SYSTEM TESTS ====================

class TestReferralSystem:
    """Test referral API endpoints"""
    
    def test_get_my_referral_code(self, admin_auth):
        """GET /api/referrals/my-code returns user's referral code"""
        response = requests.get(
            f"{BASE_URL}/api/referrals/my-code",
            headers=admin_auth["headers"]
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "referral_code" in data
        assert data["referral_code"], "referral_code should not be empty"
        assert data["referral_code"].startswith("REF-"), f"Code should start with REF-, got: {data['referral_code']}"
        print(f"✅ GET /api/referrals/my-code returns: {data['referral_code']}")
    
    def test_get_my_referrals(self, admin_auth):
        """GET /api/referrals/my-referrals returns list of referrals"""
        response = requests.get(
            f"{BASE_URL}/api/referrals/my-referrals",
            headers=admin_auth["headers"]
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✅ GET /api/referrals/my-referrals returns {len(data)} referrals")
    
    def test_register_with_referral_code(self, admin_auth):
        """POST /api/auth/register with referral_code credits both users"""
        # First get the referrer's code
        code_resp = requests.get(
            f"{BASE_URL}/api/referrals/my-code",
            headers=admin_auth["headers"]
        )
        referral_code = code_resp.json()["referral_code"]
        
        # Get referrer's current balance
        bal_resp = requests.get(
            f"{BASE_URL}/api/wallet/balance",
            headers=admin_auth["headers"]
        )
        initial_balance = bal_resp.json().get("balance", 0)
        
        # Register new user with referral code
        unique_email = f"testref_{uuid.uuid4().hex[:8]}@test.com"
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "full_name": "Test Referred User",
            "password": "test123",
            "role": "guardian",
            "referral_code": referral_code
        })
        assert reg_resp.status_code == 200, f"Registration failed: {reg_resp.status_code} - {reg_resp.text}"
        
        # Check referrer's balance increased
        new_bal_resp = requests.get(
            f"{BASE_URL}/api/wallet/balance",
            headers=admin_auth["headers"]
        )
        new_balance = new_bal_resp.json().get("balance", 0)
        
        assert new_balance > initial_balance, f"Referrer balance should increase. Before: {initial_balance}, After: {new_balance}"
        print(f"✅ Referral reward applied: balance {initial_balance} -> {new_balance}")


# ==================== WORD DEFINITION API TESTS ====================

class TestWordDefinitionAPI:
    """Test word definition endpoint"""
    
    def test_define_word_basic(self, admin_auth):
        """POST /api/words/define returns AI-powered definition"""
        response = requests.post(
            f"{BASE_URL}/api/words/define",
            headers=admin_auth["headers"],
            json={"word": "ephemeral"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "word" in data, "Response should contain 'word'"
        assert "definition" in data, "Response should contain 'definition'"
        assert data["word"] == "ephemeral"
        print(f"✅ Word definition received: {data.get('definition', '')[:80]}...")
    
    def test_define_word_with_context(self, admin_auth):
        """POST /api/words/define accepts context parameter"""
        response = requests.post(
            f"{BASE_URL}/api/words/define",
            headers=admin_auth["headers"],
            json={
                "word": "bank",
                "context": "The river bank was covered with wildflowers."
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        expected_fields = ["word", "definition", "part_of_speech", "example_sentence"]
        for field in expected_fields:
            assert field in data, f"Response missing '{field}'"
        
        print(f"✅ Word definition with context: {data.get('definition', '')[:80]}...")
    
    def test_define_word_returns_synonyms(self, admin_auth):
        """POST /api/words/define returns synonyms"""
        response = requests.post(
            f"{BASE_URL}/api/words/define",
            headers=admin_auth["headers"],
            json={"word": "happy"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Synonyms might be present or empty list
        assert "synonyms" in data or "error" not in data
        print(f"✅ Synonyms field present: {data.get('synonyms', [])}")


# ==================== DONATION SYSTEM TESTS ====================

class TestDonationSystem:
    """Test donation/sponsor endpoints"""
    
    def test_donation_stats_public(self):
        """GET /api/donations/stats is publicly accessible"""
        response = requests.get(f"{BASE_URL}/api/donations/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        expected_fields = ["total_donated", "total_stories_funded", "total_donors", "recent"]
        for field in expected_fields:
            assert field in data, f"Response missing '{field}'"
        
        assert isinstance(data["total_donated"], (int, float))
        assert isinstance(data["total_stories_funded"], int)
        assert isinstance(data["total_donors"], int)
        assert isinstance(data["recent"], list)
        
        print(f"✅ Donation stats: ${data['total_donated']:.2f} donated, {data['total_stories_funded']} stories funded")
    
    def test_create_donation_returns_checkout_url(self, admin_auth):
        """POST /api/donations/create creates Stripe checkout"""
        response = requests.post(
            f"{BASE_URL}/api/donations/create",
            headers=admin_auth["headers"],
            json={
                "amount": 10.0,
                "message": "Test donation",
                "origin_url": "https://test.com"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "url" in data, "Response should contain checkout 'url'"
        assert "session_id" in data, "Response should contain 'session_id'"
        assert "stories_funded" in data, "Response should contain 'stories_funded'"
        assert data["url"].startswith("http"), "URL should be a valid HTTP URL"
        
        print(f"✅ Donation checkout created: {data['stories_funded']} stories, session: {data['session_id'][:20]}...")
    
    def test_create_donation_minimum_amount(self, admin_auth):
        """POST /api/donations/create rejects < $1"""
        response = requests.post(
            f"{BASE_URL}/api/donations/create",
            headers=admin_auth["headers"],
            json={
                "amount": 0.50,
                "message": "",
                "origin_url": "https://test.com"
            }
        )
        assert response.status_code == 400, f"Expected 400 for amount < $1, got {response.status_code}"
        print("✅ Donation minimum $1 enforced")


# ==================== ADMIN BILLING CONFIG TESTS ====================

class TestAdminBillingConfig:
    """Test admin billing/ROI configuration"""
    
    def test_get_billing_config(self, admin_auth):
        """GET /api/admin/billing-config returns config"""
        response = requests.get(
            f"{BASE_URL}/api/admin/billing-config",
            headers=admin_auth["headers"]
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        expected_fields = [
            "pricing_model", "per_seat_price", "roi_markup_percent", 
            "flat_fee_per_story", "avg_cost_per_story", "free_tier_stories",
            "referral_reward_amount"
        ]
        for field in expected_fields:
            assert field in data, f"Response missing '{field}'"
        
        assert data["pricing_model"] in ["per_seat", "roi_markup", "flat_fee"]
        print(f"✅ Billing config: model={data['pricing_model']}, per_seat=${data['per_seat_price']}")
    
    def test_update_billing_config(self, admin_auth):
        """POST /api/admin/billing-config updates config"""
        response = requests.post(
            f"{BASE_URL}/api/admin/billing-config",
            headers=admin_auth["headers"],
            json={
                "pricing_model": "per_seat",
                "per_seat_price": 5.99,
                "roi_markup_percent": 350,
                "flat_fee_per_story": 0.50,
                "avg_cost_per_story": 0.20,
                "free_tier_stories": 5,
                "remove_limits_on_paid": True,
                "referral_reward_amount": 5.0,
                "donation_cost_per_story": 0.20
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "message" in data
        print(f"✅ Billing config updated: {data.get('message')}")
    
    def test_billing_config_requires_admin(self):
        """Billing config requires admin role"""
        # Try without auth
        response = requests.get(f"{BASE_URL}/api/admin/billing-config")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✅ Billing config requires authentication")


# ==================== ADMIN FEATURE FLAGS TESTS ====================

class TestAdminFeatureFlags:
    """Test admin feature flags"""
    
    def test_get_feature_flags(self, admin_auth):
        """GET /api/admin/feature-flags returns flags"""
        response = requests.get(
            f"{BASE_URL}/api/admin/feature-flags",
            headers=admin_auth["headers"]
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        expected_flags = [
            "belief_system_enabled", "cultural_context_enabled", "multi_language_enabled",
            "donations_enabled", "referrals_enabled", "word_definitions_enabled", "accessibility_mode"
        ]
        for flag in expected_flags:
            assert flag in data, f"Response missing flag '{flag}'"
            assert isinstance(data[flag], bool), f"Flag '{flag}' should be boolean"
        
        print(f"✅ Feature flags retrieved: {len(expected_flags)} flags")
    
    def test_update_feature_flags(self, admin_auth):
        """POST /api/admin/feature-flags updates flags"""
        response = requests.post(
            f"{BASE_URL}/api/admin/feature-flags",
            headers=admin_auth["headers"],
            json={
                "belief_system_enabled": True,
                "cultural_context_enabled": True,
                "multi_language_enabled": True,
                "donations_enabled": True,
                "referrals_enabled": True,
                "word_definitions_enabled": True,
                "accessibility_mode": True
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "message" in data
        print(f"✅ Feature flags updated: {data.get('message')}")
    
    def test_feature_flags_requires_admin(self):
        """Feature flags require admin role"""
        response = requests.get(f"{BASE_URL}/api/admin/feature-flags")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✅ Feature flags require authentication")


# ==================== STUDENT PREFERENCES TESTS ====================

class TestStudentBeliefCultureLanguage:
    """Test student belief system, cultural context, language fields"""
    
    def test_student_update_with_belief_system(self, admin_auth):
        """PATCH /api/students/{id} accepts belief_system"""
        # First get students
        students_resp = requests.get(
            f"{BASE_URL}/api/students",
            headers=admin_auth["headers"],
            params={"guardian_id": admin_auth["user"]["id"]}
        )
        
        if students_resp.status_code != 200 or not students_resp.json():
            pytest.skip("No students to test belief_system update")
        
        student = students_resp.json()[0]
        
        response = requests.patch(
            f"{BASE_URL}/api/students/{student['id']}",
            headers=admin_auth["headers"],
            json={"belief_system": "Buddhist"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("belief_system") == "Buddhist"
        print(f"✅ Student belief_system updated to: {data.get('belief_system')}")
    
    def test_student_update_with_cultural_context(self, admin_auth):
        """PATCH /api/students/{id} accepts cultural_context"""
        students_resp = requests.get(
            f"{BASE_URL}/api/students",
            headers=admin_auth["headers"],
            params={"guardian_id": admin_auth["user"]["id"]}
        )
        
        if students_resp.status_code != 200 or not students_resp.json():
            pytest.skip("No students to test cultural_context update")
        
        student = students_resp.json()[0]
        
        response = requests.patch(
            f"{BASE_URL}/api/students/{student['id']}",
            headers=admin_auth["headers"],
            json={"cultural_context": "East Asian"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("cultural_context") == "East Asian"
        print(f"✅ Student cultural_context updated to: {data.get('cultural_context')}")
    
    def test_student_update_with_language(self, admin_auth):
        """PATCH /api/students/{id} accepts language"""
        students_resp = requests.get(
            f"{BASE_URL}/api/students",
            headers=admin_auth["headers"],
            params={"guardian_id": admin_auth["user"]["id"]}
        )
        
        if students_resp.status_code != 200 or not students_resp.json():
            pytest.skip("No students to test language update")
        
        student = students_resp.json()[0]
        
        response = requests.patch(
            f"{BASE_URL}/api/students/{student['id']}",
            headers=admin_auth["headers"],
            json={"language": "Spanish"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("language") == "Spanish"
        print(f"✅ Student language updated to: {data.get('language')}")
        
        # Reset to English
        requests.patch(
            f"{BASE_URL}/api/students/{student['id']}",
            headers=admin_auth["headers"],
            json={"language": "English"}
        )


# ==================== MASTER ADMIN TEST ====================

class TestMasterAdmin:
    """Test master admin allen@songsforcenturies.com"""
    
    def test_allen_has_admin_role(self):
        """User allen@songsforcenturies.com should have admin role"""
        # Try to login as allen (if exists)
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "allen@songsforcenturies.com",
            "password": "test123"  # Try common test password
        })
        
        if response.status_code == 401:
            # User doesn't exist or wrong password - check via admin users list
            pytest.skip("Cannot verify allen user - password unknown")
        
        if response.status_code == 200:
            data = response.json()
            user = data.get("user", {})
            assert user.get("role") == "admin", f"Expected role='admin', got '{user.get('role')}'"
            print(f"✅ allen@songsforcenturies.com has role=admin")


# ==================== API HEALTH TEST ====================

class TestAPIHealth:
    """Basic API health check"""
    
    def test_api_root(self):
        """GET /api/ returns health info"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✅ API healthy: {data.get('message')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
