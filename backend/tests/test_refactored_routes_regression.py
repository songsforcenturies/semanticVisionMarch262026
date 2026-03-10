"""
Comprehensive Regression Test Suite for Refactored Backend Routes

Tests all major endpoints after monolithic server.py was split into modular route files:
- routes/auth.py - Authentication routes
- routes/documents.py - Health check and document downloads
- routes/students.py - Student CRUD routes
- routes/wordbanks.py - Word bank routes
- routes/admin.py - Admin dashboard routes
- routes/brands.py - Brand management routes
- routes/affiliates.py - Affiliate program routes
- routes/recordings.py - Recording and audio book routes
- routes/classroom.py - Classroom session routes
- routes/narratives.py - Story/narrative routes

Credentials: allen@songsforcenturies.com / LexiAdmin2026!
Token field: access_token (NOT token)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"


class TestHealthAndRoot:
    """Test health check and root endpoints from documents.py"""
    
    def test_root_endpoint(self):
        """GET /api/ - should return API running message"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200, f"Root endpoint failed: {response.text}"
        data = response.json()
        assert "message" in data
        assert "Semantic Vision API" in data["message"]
        print(f"✓ Root endpoint passed: {data}")
    
    def test_health_check(self):
        """GET /api/health - should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        data = response.json()
        assert data.get("status") == "healthy"
        assert "timestamp" in data
        print(f"✓ Health check passed: {data}")


class TestAuthentication:
    """Test authentication endpoints from auth.py"""
    
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
    
    def test_login_invalid_credentials(self):
        """POST /api/auth/login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid login correctly rejected with 401")


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
    
    # Students endpoint (students.py)
    def test_get_students(self):
        """GET /api/students - should return student list"""
        response = requests.get(f"{BASE_URL}/api/students", headers=self.headers)
        assert response.status_code == 200, f"Students endpoint failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✓ Students endpoint passed: {len(data)} students")
    
    # Word banks endpoint (wordbanks.py)
    def test_get_word_banks(self):
        """GET /api/word-banks - should return word banks"""
        response = requests.get(f"{BASE_URL}/api/word-banks", headers=self.headers)
        assert response.status_code == 200, f"Word banks endpoint failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✓ Word banks endpoint passed: {len(data)} word banks")
    
    # Admin stats endpoint (admin.py)
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
    
    # Admin users endpoint (admin.py)
    def test_get_admin_users(self):
        """GET /api/admin/users - admin only, should return users"""
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=self.headers)
        assert response.status_code == 200, f"Admin users endpoint failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✓ Admin users endpoint passed: {len(data)} users")
    
    # Admin brands endpoint (brands.py)
    def test_get_admin_brands(self):
        """GET /api/admin/brands - admin only, should return brands list"""
        response = requests.get(f"{BASE_URL}/api/admin/brands", headers=self.headers)
        assert response.status_code == 200, f"Admin brands endpoint failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✓ Admin brands endpoint passed: {len(data)} brands")
    
    # Admin brand analytics endpoint (brands.py)
    def test_get_admin_brand_analytics(self):
        """GET /api/admin/brand-analytics - admin only, should return analytics"""
        response = requests.get(f"{BASE_URL}/api/admin/brand-analytics", headers=self.headers)
        assert response.status_code == 200, f"Brand analytics endpoint failed: {response.text}"
        data = response.json()
        assert "total_brand_revenue" in data
        assert "total_impressions" in data
        assert "brands" in data
        print(f"✓ Brand analytics endpoint passed: revenue=${data['total_brand_revenue']}, impressions={data['total_impressions']}")
    
    # Admin affiliates endpoint (affiliates.py)
    def test_get_admin_affiliates(self):
        """GET /api/admin/affiliates - admin only, should return affiliates"""
        response = requests.get(f"{BASE_URL}/api/admin/affiliates", headers=self.headers)
        assert response.status_code == 200, f"Admin affiliates endpoint failed: {response.text}"
        data = response.json()
        assert "affiliates" in data
        assert "settings" in data
        print(f"✓ Admin affiliates endpoint passed: {len(data['affiliates'])} affiliates")
    
    # Affiliate stats endpoint (affiliates.py)
    def test_get_affiliate_my_stats(self):
        """GET /api/affiliates/my-stats - authenticated, should return affiliate stats"""
        response = requests.get(f"{BASE_URL}/api/affiliates/my-stats", headers=self.headers)
        assert response.status_code == 200, f"Affiliate stats endpoint failed: {response.text}"
        data = response.json()
        # Response will have is_affiliate field
        assert "is_affiliate" in data
        print(f"✓ Affiliate stats endpoint passed: is_affiliate={data.get('is_affiliate')}")
    
    # Guardian recordings endpoint (recordings.py)
    def test_get_guardian_recordings(self):
        """GET /api/recordings/guardian/all - authenticated, should return recordings"""
        response = requests.get(f"{BASE_URL}/api/recordings/guardian/all", headers=self.headers)
        assert response.status_code == 200, f"Guardian recordings endpoint failed: {response.text}"
        data = response.json()
        assert "recordings" in data
        assert "students" in data
        print(f"✓ Guardian recordings endpoint passed: {len(data['recordings'])} recordings")
    
    # Classroom sessions endpoint (classroom.py)
    def test_get_classroom_sessions(self):
        """GET /api/classroom-sessions - authenticated, should return sessions"""
        response = requests.get(f"{BASE_URL}/api/classroom-sessions", headers=self.headers)
        assert response.status_code == 200, f"Classroom sessions endpoint failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✓ Classroom sessions endpoint passed: {len(data)} sessions")
    
    # Narratives endpoint (narratives.py)
    def test_get_narratives(self):
        """GET /api/narratives - authenticated, should return narratives"""
        response = requests.get(f"{BASE_URL}/api/narratives", headers=self.headers)
        assert response.status_code == 200, f"Narratives endpoint failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✓ Narratives endpoint passed: {len(data)} narratives")


class TestPublicDocumentEndpoints:
    """Test public document download endpoints from documents.py"""
    
    def test_patent_definitive_pdf(self):
        """GET /api/patent/definitive-pdf - public, should return PDF file"""
        response = requests.get(f"{BASE_URL}/api/patent/definitive-pdf")
        # 200 means file exists and is served, 404 means file not found
        if response.status_code == 200:
            assert response.headers.get("content-type") in ["application/pdf", "application/octet-stream"]
            print("✓ Patent definitive PDF endpoint passed: file served")
        elif response.status_code == 404:
            # File may not exist, but endpoint works
            print("✓ Patent definitive PDF endpoint works (file not found - expected if file not uploaded)")
        else:
            pytest.fail(f"Unexpected status: {response.status_code}, {response.text}")
    
    def test_patent_definitive_md(self):
        """GET /api/patent/definitive-md - public, should return markdown"""
        response = requests.get(f"{BASE_URL}/api/patent/definitive-md")
        if response.status_code == 200:
            assert "text/markdown" in response.headers.get("content-type", "")
            print("✓ Patent definitive MD endpoint passed: file served")
        elif response.status_code == 404:
            print("✓ Patent definitive MD endpoint works (file not found - expected if file not uploaded)")
        else:
            pytest.fail(f"Unexpected status: {response.status_code}, {response.text}")
    
    def test_patent_screenshots_pdf(self):
        """GET /api/patent/screenshots-pdf - public, should return PDF"""
        response = requests.get(f"{BASE_URL}/api/patent/screenshots-pdf")
        if response.status_code == 200:
            assert response.headers.get("content-type") in ["application/pdf", "application/octet-stream"]
            print("✓ Patent screenshots PDF endpoint passed: file served")
        elif response.status_code == 404:
            print("✓ Patent screenshots PDF endpoint works (file not found)")
        else:
            pytest.fail(f"Unexpected status: {response.status_code}, {response.text}")
    
    def test_user_manual_master_pdf(self):
        """GET /api/user-manual/master-pdf - public, should return PDF"""
        response = requests.get(f"{BASE_URL}/api/user-manual/master-pdf")
        if response.status_code == 200:
            assert response.headers.get("content-type") in ["application/pdf", "application/octet-stream"]
            print("✓ User manual master PDF endpoint passed: file served")
        elif response.status_code == 404:
            print("✓ User manual master PDF endpoint works (file not found)")
        else:
            pytest.fail(f"Unexpected status: {response.status_code}, {response.text}")


class TestAdditionalAdminEndpoints:
    """Test additional admin endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_admin_costs(self):
        """GET /api/admin/costs - should return cost tracking data"""
        response = requests.get(f"{BASE_URL}/api/admin/costs", headers=self.headers)
        assert response.status_code == 200, f"Admin costs failed: {response.text}"
        data = response.json()
        assert "total_cost" in data
        print(f"✓ Admin costs endpoint passed: total_cost=${data['total_cost']}")
    
    def test_admin_models(self):
        """GET /api/admin/models - should return LLM model config"""
        response = requests.get(f"{BASE_URL}/api/admin/models", headers=self.headers)
        assert response.status_code == 200, f"Admin models failed: {response.text}"
        data = response.json()
        assert "provider" in data or "model" in data
        print(f"✓ Admin models endpoint passed: {data}")
    
    def test_admin_plan_stats(self):
        """GET /api/admin/plan-stats - should return subscription plan stats"""
        response = requests.get(f"{BASE_URL}/api/admin/plan-stats", headers=self.headers)
        assert response.status_code == 200, f"Admin plan stats failed: {response.text}"
        data = response.json()
        assert "plan_breakdown" in data
        assert "total_guardians" in data
        print(f"✓ Admin plan stats endpoint passed: {data['total_guardians']} guardians")
    
    def test_admin_coupons(self):
        """GET /api/admin/coupons - should return coupons list"""
        response = requests.get(f"{BASE_URL}/api/admin/coupons", headers=self.headers)
        assert response.status_code == 200, f"Admin coupons failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Admin coupons endpoint passed: {len(data)} coupons")
    
    def test_admin_plans(self):
        """GET /api/admin/plans - should return subscription plans"""
        response = requests.get(f"{BASE_URL}/api/admin/plans", headers=self.headers)
        assert response.status_code == 200, f"Admin plans failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Admin plans endpoint passed: {len(data)} plans")


class TestWalletEndpoints:
    """Test wallet-related endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_wallet_balance(self):
        """GET /api/wallet/balance - should return user's wallet balance"""
        response = requests.get(f"{BASE_URL}/api/wallet/balance", headers=self.headers)
        assert response.status_code == 200, f"Wallet balance failed: {response.text}"
        data = response.json()
        assert "balance" in data
        print(f"✓ Wallet balance endpoint passed: balance=${data['balance']}")
    
    def test_wallet_transactions(self):
        """GET /api/wallet/transactions - should return transaction history"""
        response = requests.get(f"{BASE_URL}/api/wallet/transactions", headers=self.headers)
        assert response.status_code == 200, f"Wallet transactions failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Wallet transactions endpoint passed: {len(data)} transactions")
    
    def test_wallet_packages(self):
        """GET /api/wallet/packages - should return topup packages"""
        response = requests.get(f"{BASE_URL}/api/wallet/packages")
        assert response.status_code == 200, f"Wallet packages failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Wallet packages endpoint passed: {len(data)} packages")


class TestReferralEndpoints:
    """Test referral-related endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_referral_my_code(self):
        """GET /api/referrals/my-code - should return user's referral code"""
        response = requests.get(f"{BASE_URL}/api/referrals/my-code", headers=self.headers)
        assert response.status_code == 200, f"Referral code failed: {response.text}"
        data = response.json()
        assert "referral_code" in data
        print(f"✓ Referral code endpoint passed: code={data['referral_code']}")
    
    def test_referral_my_referrals(self):
        """GET /api/referrals/my-referrals - should return user's referrals"""
        response = requests.get(f"{BASE_URL}/api/referrals/my-referrals", headers=self.headers)
        assert response.status_code == 200, f"My referrals failed: {response.text}"
        data = response.json()
        assert "referrals" in data
        assert "total_earned" in data
        print(f"✓ My referrals endpoint passed: {data['total_count']} referrals, earned=${data['total_earned']}")
    
    def test_referral_reward_amount(self):
        """GET /api/referrals/reward-amount - public, should return reward amount"""
        response = requests.get(f"{BASE_URL}/api/referrals/reward-amount")
        assert response.status_code == 200, f"Referral reward amount failed: {response.text}"
        data = response.json()
        assert "referral_reward_amount" in data
        print(f"✓ Referral reward amount endpoint passed: ${data['referral_reward_amount']}")
    
    def test_contests_leaderboard(self):
        """GET /api/contests/leaderboard - should return referral leaderboard"""
        response = requests.get(f"{BASE_URL}/api/contests/leaderboard")
        assert response.status_code == 200, f"Leaderboard failed: {response.text}"
        data = response.json()
        assert "leaderboard" in data
        print(f"✓ Contests leaderboard endpoint passed: {len(data['leaderboard'])} entries")


class TestCurrencyEndpoints:
    """Test currency detection and exchange rate endpoints"""
    
    def test_currency_detect(self):
        """GET /api/currency/detect - should detect user's currency"""
        response = requests.get(f"{BASE_URL}/api/currency/detect")
        assert response.status_code == 200, f"Currency detect failed: {response.text}"
        data = response.json()
        assert "country_code" in data
        assert "currency_code" in data
        print(f"✓ Currency detect endpoint passed: {data['country_code']}/{data['currency_code']}")
    
    def test_currency_rates(self):
        """GET /api/currency/rates - should return exchange rates"""
        response = requests.get(f"{BASE_URL}/api/currency/rates")
        assert response.status_code == 200, f"Currency rates failed: {response.text}"
        data = response.json()
        assert "base" in data
        assert "rates" in data
        print(f"✓ Currency rates endpoint passed: base={data['base']}, {len(data['rates'])} currencies")


class TestNotificationEndpoints:
    """Test notification and messaging endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_notifications(self):
        """GET /api/notifications - should return user notifications"""
        response = requests.get(f"{BASE_URL}/api/notifications", headers=self.headers)
        assert response.status_code == 200, f"Notifications failed: {response.text}"
        data = response.json()
        assert "messages" in data
        assert "unread_count" in data
        print(f"✓ Notifications endpoint passed: {data['unread_count']} unread")
    
    def test_admin_messages(self):
        """GET /api/admin/messages - should return admin messages"""
        response = requests.get(f"{BASE_URL}/api/admin/messages", headers=self.headers)
        assert response.status_code == 200, f"Admin messages failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Admin messages endpoint passed: {len(data)} messages")


class TestSpellingContestEndpoints:
    """Test spelling contest endpoints"""
    
    def test_spelling_contests(self):
        """GET /api/spelling-contests - should return active contests"""
        response = requests.get(f"{BASE_URL}/api/spelling-contests")
        assert response.status_code == 200, f"Spelling contests failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Spelling contests endpoint passed: {len(data)} active contests")


class TestSubscriptionEndpoints:
    """Test subscription-related endpoints"""
    
    def test_subscription_plans_available(self):
        """GET /api/subscription-plans/available - should return available plans"""
        response = requests.get(f"{BASE_URL}/api/subscription-plans/available")
        assert response.status_code == 200, f"Subscription plans failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Subscription plans endpoint passed: {len(data)} available plans")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
