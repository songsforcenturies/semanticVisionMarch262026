"""
Test Iteration 36: Public Affiliate Signup + Coupon & Wallet Credit System
Features to test:
1. Public affiliate signup (POST /api/affiliates/signup)
2. Coupon CRUD (admin create/list coupons)
3. Coupon redemption (wallet_credit and percentage_discount types)
4. Wallet balance and transaction history
5. Duplicate redemption blocking
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"

class TestAffiliateSignup:
    """Test public affiliate signup page flow"""
    
    def test_affiliate_signup_success(self):
        """Test successful affiliate signup with unique email"""
        unique_email = f"testaffiliate_{uuid.uuid4().hex[:8]}@example.com"
        response = requests.post(
            f"{BASE_URL}/api/affiliates/signup",
            json={"full_name": "Test Affiliate User", "email": unique_email}
        )
        print(f"Affiliate signup response: {response.status_code}, {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert "affiliate_code" in data
        assert data["affiliate_code"].startswith("AFF-")
        assert len(data["affiliate_code"]) >= 10  # AFF-XXXXXXXX format (varies)
        assert "confirmed" in data
        print(f"PASSED: Affiliate signup - code: {data['affiliate_code']}, confirmed: {data['confirmed']}")
    
    def test_affiliate_signup_duplicate_email(self):
        """Test that duplicate email affiliate signup returns error"""
        # First signup
        unique_email = f"testdup_{uuid.uuid4().hex[:8]}@example.com"
        response1 = requests.post(
            f"{BASE_URL}/api/affiliates/signup",
            json={"full_name": "First User", "email": unique_email}
        )
        assert response1.status_code == 200
        
        # Second signup with same email
        response2 = requests.post(
            f"{BASE_URL}/api/affiliates/signup",
            json={"full_name": "Second User", "email": unique_email}
        )
        print(f"Duplicate signup response: {response2.status_code}, {response2.json()}")
        assert response2.status_code == 400
        assert "already registered" in response2.json().get("detail", "").lower()
        print("PASSED: Duplicate email affiliate signup returns proper error")
    
    def test_affiliate_signup_missing_fields(self):
        """Test that signup without required fields fails"""
        response = requests.post(
            f"{BASE_URL}/api/affiliates/signup",
            json={"full_name": "No Email User"}
        )
        assert response.status_code == 400
        print("PASSED: Missing email field returns 400 error")
        
        response2 = requests.post(
            f"{BASE_URL}/api/affiliates/signup",
            json={"email": "nofullname@test.com"}
        )
        assert response2.status_code == 400
        print("PASSED: Missing full_name field returns 400 error")


class TestAdminLogin:
    """Helper to get admin token"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        token = data.get("access_token")
        assert token, "No access_token in login response"
        print(f"PASSED: Admin login successful, user: {data['user']['full_name']}")
        return token


class TestCouponSystem(TestAdminLogin):
    """Test coupon CRUD and redemption"""
    
    def test_admin_list_coupons(self, admin_token):
        """Test admin can list all coupons"""
        response = requests.get(
            f"{BASE_URL}/api/admin/coupons",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        print(f"List coupons response: {response.status_code}")
        assert response.status_code == 200
        coupons = response.json()
        assert isinstance(coupons, list)
        print(f"PASSED: Admin can list coupons - found {len(coupons)} coupons")
        return coupons
    
    def test_admin_create_wallet_credit_coupon(self, admin_token):
        """Test admin can create a wallet_credit coupon"""
        unique_code = f"TEST{uuid.uuid4().hex[:6].upper()}"
        response = requests.post(
            f"{BASE_URL}/api/admin/coupons",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "code": unique_code,
                "coupon_type": "wallet_credit",
                "value": 5.0,
                "max_uses": 10,
                "description": "Test wallet credit coupon"
            }
        )
        print(f"Create wallet_credit coupon response: {response.status_code}, {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == unique_code
        assert data["coupon_type"] == "wallet_credit"
        assert data["value"] == 5.0
        print(f"PASSED: Created wallet_credit coupon: {unique_code}")
        return unique_code
    
    def test_admin_create_percentage_discount_coupon(self, admin_token):
        """Test admin can create a percentage_discount coupon"""
        unique_code = f"DISC{uuid.uuid4().hex[:6].upper()}"
        response = requests.post(
            f"{BASE_URL}/api/admin/coupons",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "code": unique_code,
                "coupon_type": "percentage_discount",
                "value": 25.0,
                "max_uses": 5,
                "description": "Test 25% discount coupon"
            }
        )
        print(f"Create percentage_discount coupon response: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert data["coupon_type"] == "percentage_discount"
        assert data["value"] == 25.0
        print(f"PASSED: Created percentage_discount coupon: {unique_code}")
        return unique_code


class TestCouponRedemption(TestAdminLogin):
    """Test coupon redemption flow"""
    
    @pytest.fixture(scope="class")
    def test_coupon_code(self, admin_token):
        """Create a test coupon for redemption tests"""
        unique_code = f"REDEEM{uuid.uuid4().hex[:4].upper()}"
        response = requests.post(
            f"{BASE_URL}/api/admin/coupons",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "code": unique_code,
                "coupon_type": "wallet_credit",
                "value": 7.50,
                "max_uses": 100,
                "description": "Redemption test coupon"
            }
        )
        assert response.status_code == 200
        return unique_code
    
    def test_redeem_wallet_credit_coupon(self, admin_token, test_coupon_code):
        """Test redeeming a wallet_credit coupon adds to balance"""
        # Get initial balance
        balance_resp = requests.get(
            f"{BASE_URL}/api/wallet/balance",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert balance_resp.status_code == 200
        initial_balance = balance_resp.json().get("balance", 0)
        print(f"Initial wallet balance: ${initial_balance}")
        
        # Redeem coupon
        redeem_resp = requests.post(
            f"{BASE_URL}/api/coupons/redeem",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"code": test_coupon_code}
        )
        print(f"Redeem response: {redeem_resp.status_code}, {redeem_resp.json()}")
        assert redeem_resp.status_code == 200
        assert "wallet" in redeem_resp.json().get("message", "").lower()
        
        # Verify balance increased
        new_balance_resp = requests.get(
            f"{BASE_URL}/api/wallet/balance",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        new_balance = new_balance_resp.json().get("balance", 0)
        print(f"New wallet balance: ${new_balance}")
        assert new_balance >= initial_balance + 7.50
        print(f"PASSED: Wallet balance increased from ${initial_balance} to ${new_balance}")
    
    def test_duplicate_redemption_blocked(self, admin_token, test_coupon_code):
        """Test that same user cannot redeem same coupon twice"""
        redeem_resp = requests.post(
            f"{BASE_URL}/api/coupons/redeem",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"code": test_coupon_code}
        )
        print(f"Duplicate redemption response: {redeem_resp.status_code}, {redeem_resp.json()}")
        assert redeem_resp.status_code == 400
        assert "already redeemed" in redeem_resp.json().get("detail", "").lower()
        print("PASSED: Duplicate coupon redemption is properly blocked")
    
    def test_invalid_coupon_error(self, admin_token):
        """Test invalid coupon code returns proper error"""
        redeem_resp = requests.post(
            f"{BASE_URL}/api/coupons/redeem",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"code": "FAKECODE12345"}
        )
        print(f"Invalid coupon response: {redeem_resp.status_code}")
        assert redeem_resp.status_code == 404
        assert "invalid" in redeem_resp.json().get("detail", "").lower() or "expired" in redeem_resp.json().get("detail", "").lower()
        print("PASSED: Invalid coupon code returns proper error")


class TestWalletSystem(TestAdminLogin):
    """Test wallet balance and transactions"""
    
    def test_get_wallet_balance(self, admin_token):
        """Test getting wallet balance"""
        response = requests.get(
            f"{BASE_URL}/api/wallet/balance",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        print(f"Wallet balance response: {response.status_code}, {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert "balance" in data
        assert isinstance(data["balance"], (int, float))
        print(f"PASSED: Wallet balance endpoint works - balance: ${data['balance']}")
    
    def test_get_wallet_transactions(self, admin_token):
        """Test getting wallet transaction history"""
        response = requests.get(
            f"{BASE_URL}/api/wallet/transactions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        print(f"Wallet transactions response: {response.status_code}")
        assert response.status_code == 200
        transactions = response.json()
        assert isinstance(transactions, list)
        print(f"PASSED: Wallet transactions endpoint works - {len(transactions)} transactions found")
        
        # Verify transaction structure if any exist
        if len(transactions) > 0:
            txn = transactions[0]
            assert "type" in txn
            assert "amount" in txn
            assert "description" in txn
            print(f"Transaction structure verified: type={txn['type']}, amount=${txn['amount']}")
    
    def test_wallet_packages(self, admin_token):
        """Test getting available wallet top-up packages"""
        response = requests.get(
            f"{BASE_URL}/api/wallet/packages",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        print(f"Wallet packages response: {response.status_code}")
        assert response.status_code == 200
        packages = response.json()
        assert isinstance(packages, list)
        print(f"PASSED: Wallet packages endpoint works - {len(packages)} packages available")


class TestExistingCoupons(TestAdminLogin):
    """Test existing coupons from the system"""
    
    def test_existing_coupons_structure(self, admin_token):
        """Verify existing coupons have proper structure"""
        response = requests.get(
            f"{BASE_URL}/api/admin/coupons",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        coupons = response.json()
        
        # Print all coupon codes for reference
        print(f"\nExisting coupons in system:")
        for c in coupons[:10]:  # Show first 10
            print(f"  - {c['code']}: {c['coupon_type']}, value={c['value']}, uses={c['uses_count']}/{c['max_uses']}")
        
        # Verify at least one exists
        assert len(coupons) > 0, "Expected at least one coupon in system"
        
        # Verify structure
        for coupon in coupons:
            assert "code" in coupon
            assert "coupon_type" in coupon
            assert "value" in coupon
            assert "max_uses" in coupon
            assert "uses_count" in coupon
            assert "is_active" in coupon
        
        print(f"PASSED: {len(coupons)} coupons verified with proper structure")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
