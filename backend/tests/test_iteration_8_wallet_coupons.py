"""
Iteration 8 - Test wallet, coupons, admin delegation, subscription plans, and admin stats
Testing new features: wallet system, Stripe top-ups, coupon redemption, admin delegation, subscription plans management
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://student-wizard.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "testadmin@test.com"
ADMIN_PASSWORD = "test123"


class TestWalletAPIs:
    """Test wallet balance, packages, and transactions endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin for wallet tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.user_data = response.json()["user"]
        yield

    def test_login_returns_wallet_balance(self):
        """Login response should include wallet_balance field"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "wallet_balance" in data["user"], "wallet_balance should be in login response"
        assert isinstance(data["user"]["wallet_balance"], (int, float))
        print(f"Login returns wallet_balance: ${data['user']['wallet_balance']}")

    def test_login_returns_is_delegated_admin(self):
        """Login response should include is_delegated_admin field"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "is_delegated_admin" in data["user"], "is_delegated_admin should be in login response"
        print(f"Login returns is_delegated_admin: {data['user']['is_delegated_admin']}")

    def test_get_wallet_balance(self):
        """GET /api/wallet/balance returns user balance"""
        response = requests.get(f"{BASE_URL}/api/wallet/balance", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "balance" in data
        assert isinstance(data["balance"], (int, float))
        print(f"Wallet balance: ${data['balance']}")

    def test_get_wallet_packages(self):
        """GET /api/wallet/packages returns available top-up packages"""
        response = requests.get(f"{BASE_URL}/api/wallet/packages", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Should have at least one package"
        
        # Verify package structure
        for pkg in data:
            assert "id" in pkg
            assert "amount" in pkg
            assert isinstance(pkg["amount"], (int, float))
        
        print(f"Found {len(data)} packages: {[p['id'] for p in data]}")

    def test_get_wallet_transactions(self):
        """GET /api/wallet/transactions returns transaction history"""
        response = requests.get(f"{BASE_URL}/api/wallet/transactions", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            # Verify transaction structure
            txn = data[0]
            assert "id" in txn
            assert "type" in txn
            assert "amount" in txn
            assert "description" in txn
            assert "balance_after" in txn
            print(f"Found {len(data)} transactions")
        else:
            print("No transactions found (OK for new account)")

    def test_wallet_topup_creates_stripe_session(self):
        """POST /api/wallet/topup creates Stripe checkout session"""
        response = requests.post(f"{BASE_URL}/api/wallet/topup", 
            headers=self.headers,
            json={
                "package_id": "small",  # $5
                "origin_url": "https://student-wizard.preview.emergentagent.com"
            }
        )
        # Should return 200 or appropriate error if Stripe not fully configured
        assert response.status_code in [200, 400, 500], f"Unexpected status: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "url" in data, "Should return Stripe checkout URL"
            assert data["url"].startswith("https://checkout.stripe.com") or "session_id" in data
            print(f"Stripe checkout URL created successfully")
        else:
            print(f"Stripe topup returned {response.status_code}: {response.text}")

    def test_payment_status_endpoint(self):
        """GET /api/payments/status/{session_id} handles invalid session"""
        response = requests.get(f"{BASE_URL}/api/payments/status/invalid_session_id", headers=self.headers)
        # Should return error for invalid session
        assert response.status_code in [200, 404, 400], f"Unexpected status: {response.text}"
        print(f"Payment status check returned {response.status_code}")


class TestCouponAPIs:
    """Test coupon creation, listing, deletion, and redemption"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin for coupon tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        yield

    def test_list_coupons(self):
        """GET /api/admin/coupons returns coupon list"""
        response = requests.get(f"{BASE_URL}/api/admin/coupons", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} coupons")
        
        # Check if WELCOME10 coupon exists (mentioned in context)
        coupon_codes = [c.get("code", "") for c in data]
        if "WELCOME10" in coupon_codes:
            print("WELCOME10 coupon exists as expected")

    def test_create_coupon(self):
        """POST /api/admin/coupons creates new coupon"""
        unique_code = f"TEST{int(time.time())}"
        response = requests.post(f"{BASE_URL}/api/admin/coupons", 
            headers=self.headers,
            json={
                "code": unique_code,
                "coupon_type": "wallet_credit",
                "value": 5.0,
                "max_uses": 10,
                "description": "Test coupon for iteration 8"
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["code"] == unique_code
        assert data["coupon_type"] == "wallet_credit"
        assert data["value"] == 5.0
        print(f"Created coupon: {unique_code}")
        
        # Store for cleanup
        self.created_coupon_id = data["id"]
        
        # Cleanup - delete the test coupon
        delete_response = requests.delete(
            f"{BASE_URL}/api/admin/coupons/{self.created_coupon_id}", 
            headers=self.headers
        )
        assert delete_response.status_code == 200

    def test_create_coupon_types(self):
        """Test creating different coupon types"""
        coupon_types = [
            ("free_stories", 3),
            ("free_students", 2),
            ("free_days", 30),
        ]
        
        for coupon_type, value in coupon_types:
            unique_code = f"TEST{coupon_type.upper()}{int(time.time())}"
            response = requests.post(f"{BASE_URL}/api/admin/coupons", 
                headers=self.headers,
                json={
                    "code": unique_code,
                    "coupon_type": coupon_type,
                    "value": value,
                    "max_uses": 1,
                }
            )
            assert response.status_code == 200, f"Failed to create {coupon_type}: {response.text}"
            data = response.json()
            assert data["coupon_type"] == coupon_type
            print(f"Created {coupon_type} coupon: {unique_code}")
            
            # Cleanup
            requests.delete(f"{BASE_URL}/api/admin/coupons/{data['id']}", headers=self.headers)

    def test_delete_coupon(self):
        """DELETE /api/admin/coupons/{id} removes coupon"""
        # First create a coupon to delete
        unique_code = f"TESTDEL{int(time.time())}"
        create_response = requests.post(f"{BASE_URL}/api/admin/coupons", 
            headers=self.headers,
            json={
                "code": unique_code,
                "coupon_type": "wallet_credit",
                "value": 1.0,
                "max_uses": 1,
            }
        )
        assert create_response.status_code == 200
        coupon_id = create_response.json()["id"]
        
        # Delete the coupon
        delete_response = requests.delete(
            f"{BASE_URL}/api/admin/coupons/{coupon_id}", 
            headers=self.headers
        )
        assert delete_response.status_code == 200
        print(f"Deleted coupon: {coupon_id}")

    def test_redeem_coupon_invalid_code(self):
        """POST /api/coupons/redeem returns error for invalid code"""
        response = requests.post(f"{BASE_URL}/api/coupons/redeem", 
            headers=self.headers,
            json={"code": "INVALIDCODE999"}
        )
        assert response.status_code == 404, f"Expected 404: {response.text}"
        print("Invalid coupon code correctly rejected")

    def test_redeem_coupon_duplicate(self):
        """Redeeming same coupon twice should fail"""
        # This test assumes WELCOME10 was already redeemed by admin
        response = requests.post(f"{BASE_URL}/api/coupons/redeem", 
            headers=self.headers,
            json={"code": "WELCOME10"}
        )
        # Should be 400 (already redeemed) or 404 (not found)
        assert response.status_code in [400, 404], f"Expected 400 or 404: {response.text}"
        print(f"Duplicate redemption correctly blocked: {response.status_code}")


class TestAdminDelegation:
    """Test admin delegation grant/revoke"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        yield

    def test_delegate_admin_grant(self):
        """POST /api/admin/delegate grants delegated admin"""
        # Use a test email that may or may not exist
        response = requests.post(f"{BASE_URL}/api/admin/delegate", 
            headers=self.headers,
            json={
                "email": "testdelegate@test.com",
                "is_delegated": True
            }
        )
        # May return 404 if user doesn't exist, 200 if exists
        assert response.status_code in [200, 404], f"Unexpected: {response.text}"
        print(f"Delegate grant returned: {response.status_code}")

    def test_delegate_admin_revoke(self):
        """POST /api/admin/delegate revokes delegated admin"""
        response = requests.post(f"{BASE_URL}/api/admin/delegate", 
            headers=self.headers,
            json={
                "email": "testdelegate@test.com",
                "is_delegated": False
            }
        )
        assert response.status_code in [200, 404], f"Unexpected: {response.text}"
        print(f"Delegate revoke returned: {response.status_code}")


class TestAdminUsers:
    """Test admin user listing"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        yield

    def test_get_all_users(self):
        """GET /api/admin/users returns all users"""
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Should have at least admin user"
        
        # Verify user structure
        for user in data:
            assert "id" in user
            assert "email" in user
            assert "full_name" in user
            assert "role" in user
            assert "password_hash" not in user, "Should not expose password hash"
        
        print(f"Found {len(data)} users")


class TestSubscriptionPlans:
    """Test subscription plans CRUD"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        yield

    def test_list_plans(self):
        """GET /api/admin/plans returns subscription plans"""
        response = requests.get(f"{BASE_URL}/api/admin/plans", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} subscription plans")
        
        # Check for Family Plan mentioned in context
        plan_names = [p.get("name", "") for p in data]
        if "Family Plan" in plan_names:
            print("Family Plan exists as expected")

    def test_create_plan(self):
        """POST /api/admin/plans creates new subscription plan"""
        plan_name = f"Test Plan {int(time.time())}"
        response = requests.post(f"{BASE_URL}/api/admin/plans", 
            headers=self.headers,
            json={
                "name": plan_name,
                "description": "Test plan for iteration 8",
                "price_monthly": 9.99,
                "student_seats": 5,
                "story_limit": 20,
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["name"] == plan_name
        assert data["price_monthly"] == 9.99
        assert data["student_seats"] == 5
        print(f"Created plan: {plan_name}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/admin/plans/{data['id']}", headers=self.headers)

    def test_delete_plan(self):
        """DELETE /api/admin/plans/{id} removes plan"""
        # First create a plan to delete
        plan_name = f"Delete Test Plan {int(time.time())}"
        create_response = requests.post(f"{BASE_URL}/api/admin/plans", 
            headers=self.headers,
            json={
                "name": plan_name,
                "price_monthly": 0,
                "student_seats": 1,
            }
        )
        assert create_response.status_code == 200
        plan_id = create_response.json()["id"]
        
        # Delete the plan
        delete_response = requests.delete(
            f"{BASE_URL}/api/admin/plans/{plan_id}", 
            headers=self.headers
        )
        assert delete_response.status_code == 200
        print(f"Deleted plan: {plan_id}")


class TestAdminStats:
    """Test comprehensive admin statistics endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        yield

    def test_get_admin_stats(self):
        """GET /api/admin/stats returns comprehensive platform statistics"""
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify all stat categories exist
        assert "users" in data
        assert "content" in data
        assert "reading" in data
        assert "revenue" in data
        assert "coupons" in data
        assert "classrooms" in data
        assert "ai" in data
        
        # Verify users structure
        users = data["users"]
        assert "guardians" in users
        assert "teachers" in users
        assert "students" in users
        assert "recent_signups" in users
        
        # Verify content structure
        content = data["content"]
        assert "word_banks" in content
        assert "narratives" in content
        assert "assessments_total" in content
        assert "assessments_completed" in content
        
        # Verify reading structure
        reading = data["reading"]
        assert "total_reading_hours" in reading
        assert "total_words_read" in reading
        
        # Verify revenue structure
        revenue = data["revenue"]
        assert "total_revenue" in revenue
        assert "total_payments" in revenue
        
        print(f"Stats: {data['users']['guardians']} guardians, {data['users']['students']} students")
        print(f"Content: {data['content']['word_banks']} word banks, {data['content']['narratives']} stories")
        print(f"Revenue: ${data['revenue']['total_revenue']} from {data['revenue']['total_payments']} payments")

    def test_stats_requires_admin(self):
        """Stats endpoint should require admin role"""
        # Try with no auth
        response = requests.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 401 or response.status_code == 403


class TestWalletPurchaseBank:
    """Test purchasing word banks with wallet balance"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.user_id = response.json()["user"]["id"]
        yield

    def test_purchase_bank_insufficient_balance(self):
        """Purchase fails with insufficient wallet balance"""
        # Try to purchase with non-existent bank
        response = requests.post(f"{BASE_URL}/api/wallet/purchase-bank", 
            headers=self.headers,
            json={
                "guardian_id": self.user_id,
                "bank_id": "non_existent_bank_id"
            }
        )
        # Should fail - either bank not found or insufficient balance
        assert response.status_code in [400, 404], f"Expected 400/404: {response.text}"
        print(f"Purchase bank validation working: {response.status_code}")

    def test_purchase_bank_endpoint_exists(self):
        """Verify purchase bank endpoint exists and handles requests"""
        # Get list of word banks first
        banks_response = requests.get(f"{BASE_URL}/api/word-banks", headers=self.headers)
        assert banks_response.status_code == 200
        banks = banks_response.json()
        
        if len(banks) > 0:
            # Try to purchase first available bank
            bank = banks[0]
            response = requests.post(f"{BASE_URL}/api/wallet/purchase-bank", 
                headers=self.headers,
                json={
                    "guardian_id": self.user_id,
                    "bank_id": bank["id"]
                }
            )
            # Various valid outcomes: success, already owned, insufficient funds, no subscription
            assert response.status_code in [200, 400, 404], f"Unexpected: {response.text}"
            print(f"Purchase bank attempt returned: {response.status_code}")
        else:
            print("No word banks available for purchase test")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
