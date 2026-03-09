"""
Test Suite for Iteration 32: Affiliate System & Brand Offers
Tests:
- Affiliate signup (public endpoint)
- Affiliate tracking
- Admin affiliates management
- Admin affiliate settings
- Admin affiliate update
- Admin affiliate payout
- Brand offers CRUD
- Parent offers view
- Parent offer preferences
- Offer click tracking
- Affiliate code handling during registration
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")


class TestAffiliateSignup:
    """Test public affiliate signup endpoint"""

    def test_affiliate_signup_success(self):
        """Test successful affiliate signup"""
        test_email = f"test_aff_{uuid.uuid4().hex[:8]}@example.com"
        response = requests.post(f"{BASE_URL}/api/affiliates/signup", json={
            "email": test_email,
            "full_name": "Test Affiliate User"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "affiliate_code" in data
        assert data["affiliate_code"].startswith("AFF-")
        assert "message" in data
        print(f"✓ Affiliate signup successful. Code: {data['affiliate_code']}")
        return data["affiliate_code"]

    def test_affiliate_signup_missing_fields(self):
        """Test affiliate signup with missing required fields"""
        response = requests.post(f"{BASE_URL}/api/affiliates/signup", json={
            "email": "test@example.com"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Affiliate signup correctly rejects missing full_name")

    def test_affiliate_signup_duplicate_email(self):
        """Test affiliate signup with already registered email"""
        test_email = f"test_dup_{uuid.uuid4().hex[:8]}@example.com"
        # First signup
        requests.post(f"{BASE_URL}/api/affiliates/signup", json={
            "email": test_email, "full_name": "Test Duplicate"
        })
        # Duplicate signup
        response = requests.post(f"{BASE_URL}/api/affiliates/signup", json={
            "email": test_email, "full_name": "Test Duplicate Again"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "already registered" in response.json().get("detail", "").lower()
        print("✓ Affiliate signup correctly rejects duplicate email")


class TestAffiliateTracking:
    """Test affiliate tracking endpoint"""

    def test_track_valid_affiliate_code(self):
        """Test tracking a valid affiliate code"""
        # First create an affiliate
        test_email = f"test_track_{uuid.uuid4().hex[:8]}@example.com"
        signup_resp = requests.post(f"{BASE_URL}/api/affiliates/signup", json={
            "email": test_email, "full_name": "Test Tracker"
        })
        assert signup_resp.status_code == 200
        affiliate_code = signup_resp.json()["affiliate_code"]
        
        # Track the code
        response = requests.get(f"{BASE_URL}/api/affiliates/track/{affiliate_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("valid") is True
        assert data.get("affiliate_code") == affiliate_code
        print(f"✓ Affiliate tracking works for code: {affiliate_code}")

    def test_track_invalid_affiliate_code(self):
        """Test tracking an invalid affiliate code"""
        response = requests.get(f"{BASE_URL}/api/affiliates/track/INVALID-CODE-123")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Affiliate tracking correctly rejects invalid code")


class TestAdminAffiliateManagement:
    """Test admin affiliate management endpoints"""

    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "allen@songsforcenturies.com",
            "password": "LexiAdmin2026!"
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return response.json()["access_token"]

    def test_admin_get_affiliates(self, admin_token):
        """Test admin can get all affiliates"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/affiliates", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "affiliates" in data
        assert "settings" in data
        assert isinstance(data["affiliates"], list)
        print(f"✓ Admin can fetch affiliates. Count: {len(data['affiliates'])}")

    def test_admin_update_affiliate_settings(self, admin_token):
        """Test admin can update affiliate program settings"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        settings = {
            "default_reward_type": "flat_fee",
            "default_flat_fee": 7.5,
            "default_percentage": 15.0,
            "default_wallet_credits": 6.0,
            "min_payout_threshold": 30.0,
            "affiliate_program_enabled": True,
            "auto_approve": True
        }
        response = requests.put(f"{BASE_URL}/api/admin/affiliates/settings", 
                                json=settings, headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ Admin can update affiliate settings")

    def test_admin_update_affiliate(self, admin_token):
        """Test admin can update individual affiliate"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # First create an affiliate
        test_email = f"test_admin_update_{uuid.uuid4().hex[:8]}@example.com"
        signup_resp = requests.post(f"{BASE_URL}/api/affiliates/signup", json={
            "email": test_email, "full_name": "Admin Update Test"
        })
        assert signup_resp.status_code == 200
        
        # Get affiliates to find the ID
        list_resp = requests.get(f"{BASE_URL}/api/admin/affiliates", headers=headers)
        affiliates = list_resp.json()["affiliates"]
        affiliate = next((a for a in affiliates if a["email"] == test_email), None)
        assert affiliate is not None, "Created affiliate not found"
        
        # Update the affiliate
        response = requests.put(f"{BASE_URL}/api/admin/affiliates/{affiliate['id']}", 
                                json={"flat_fee_amount": 10.0, "is_active": True, "_skip_email": True},
                                headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Admin can update affiliate: {affiliate['id']}")

    def test_admin_payout_affiliate(self, admin_token):
        """Test admin can record affiliate payout"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create affiliate with some pending balance
        test_email = f"test_payout_{uuid.uuid4().hex[:8]}@example.com"
        signup_resp = requests.post(f"{BASE_URL}/api/affiliates/signup", json={
            "email": test_email, "full_name": "Payout Test"
        })
        assert signup_resp.status_code == 200
        affiliate_code = signup_resp.json()["affiliate_code"]
        
        # Register a user with this affiliate code to generate balance
        user_email = f"referred_{uuid.uuid4().hex[:8]}@example.com"
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": user_email,
            "full_name": "Referred User",
            "password": "TestPass123!",
            "referral_code": affiliate_code
        })
        
        # Get affiliate ID and check balance
        list_resp = requests.get(f"{BASE_URL}/api/admin/affiliates", headers=headers)
        affiliates = list_resp.json()["affiliates"]
        affiliate = next((a for a in affiliates if a["email"] == test_email), None)
        
        if affiliate and affiliate.get("pending_balance", 0) > 0:
            # Record payout
            payout_amount = affiliate["pending_balance"]
            response = requests.post(f"{BASE_URL}/api/admin/affiliates/{affiliate['id']}/payout", 
                                     json={"amount": payout_amount}, headers=headers)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            print(f"✓ Admin can record payout: ${payout_amount}")
        else:
            print("✓ Payout test skipped (no pending balance)")

    def test_admin_payout_exceeds_balance(self, admin_token):
        """Test payout rejection when amount exceeds balance"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        test_email = f"test_exceed_{uuid.uuid4().hex[:8]}@example.com"
        signup_resp = requests.post(f"{BASE_URL}/api/affiliates/signup", json={
            "email": test_email, "full_name": "Exceed Test"
        })
        
        list_resp = requests.get(f"{BASE_URL}/api/admin/affiliates", headers=headers)
        affiliates = list_resp.json()["affiliates"]
        affiliate = next((a for a in affiliates if a["email"] == test_email), None)
        
        if affiliate:
            response = requests.post(f"{BASE_URL}/api/admin/affiliates/{affiliate['id']}/payout", 
                                     json={"amount": 999999}, headers=headers)
            assert response.status_code == 400, f"Expected 400, got {response.status_code}"
            print("✓ Payout correctly rejects amount exceeding balance")


class TestBrandOffersCRUD:
    """Test brand offers CRUD endpoints"""

    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "allen@songsforcenturies.com",
            "password": "LexiAdmin2026!"
        })
        assert response.status_code == 200
        return response.json()["access_token"]

    @pytest.fixture(scope="class")
    def brand_id(self, admin_token):
        """Get or create a test brand"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        # Get existing brands
        resp = requests.get(f"{BASE_URL}/api/admin/brands", headers=headers)
        if resp.status_code == 200 and resp.json():
            return resp.json()[0]["id"]
        # Create brand if none exist
        brand_data = {
            "name": f"TestBrand_{uuid.uuid4().hex[:6]}",
            "description": "Test brand for offers",
            "category": "education"
        }
        create_resp = requests.post(f"{BASE_URL}/api/admin/brands", json=brand_data, headers=headers)
        return create_resp.json()["id"]

    def test_create_brand_offer(self, admin_token, brand_id):
        """Test creating a brand offer"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        offer_data = {
            "brand_id": brand_id,
            "title": f"Test Offer {uuid.uuid4().hex[:6]}",
            "description": "50% off educational materials",
            "offer_type": "free",
            "external_link": "https://example.com/offer",
            "internal_promo_code": "TESTCODE50",
            "target_all_users": True
        }
        response = requests.post(f"{BASE_URL}/api/brands/offers", json=offer_data, headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["title"] == offer_data["title"]
        print(f"✓ Brand offer created: {data['id']}")
        return data["id"]

    def test_get_brand_offers(self, admin_token):
        """Test getting brand offers"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/brands/offers", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert isinstance(response.json(), list)
        print(f"✓ Brand offers fetched. Count: {len(response.json())}")

    def test_update_brand_offer(self, admin_token, brand_id):
        """Test updating a brand offer"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # First create an offer
        offer_data = {
            "brand_id": brand_id,
            "title": "Update Test Offer",
            "description": "Original description",
            "offer_type": "free"
        }
        create_resp = requests.post(f"{BASE_URL}/api/brands/offers", json=offer_data, headers=headers)
        offer_id = create_resp.json()["id"]
        
        # Update the offer
        update_data = {"title": "Updated Offer Title", "is_active": False}
        response = requests.put(f"{BASE_URL}/api/brands/offers/{offer_id}", json=update_data, headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ Brand offer updated: {offer_id}")

    def test_delete_brand_offer(self, admin_token, brand_id):
        """Test deleting a brand offer"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create an offer to delete
        offer_data = {
            "brand_id": brand_id,
            "title": "Delete Test Offer",
            "description": "Will be deleted",
            "offer_type": "free"
        }
        create_resp = requests.post(f"{BASE_URL}/api/brands/offers", json=offer_data, headers=headers)
        offer_id = create_resp.json()["id"]
        
        # Delete the offer
        response = requests.delete(f"{BASE_URL}/api/brands/offers/{offer_id}", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ Brand offer deleted: {offer_id}")


class TestParentOffers:
    """Test parent-facing offers endpoints"""

    @pytest.fixture(scope="class")
    def parent_token(self):
        """Get or create parent auth token"""
        test_email = f"test_parent_{uuid.uuid4().hex[:8]}@example.com"
        # Try to register
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "full_name": "Test Parent",
            "password": "TestPass123!",
            "role": "guardian"
        })
        if reg_resp.status_code == 400:
            # Already exists, try login with existing
            test_email = "allen@songsforcenturies.com"
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": test_email,
                "password": "LexiAdmin2026!"
            })
            return login_resp.json()["access_token"]
        
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_email,
            "password": "TestPass123!"
        })
        return login_resp.json()["access_token"]

    def test_get_available_offers(self, parent_token):
        """Test parent can get available offers"""
        headers = {"Authorization": f"Bearer {parent_token}"}
        response = requests.get(f"{BASE_URL}/api/offers", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "offers_enabled" in data
        assert "offers" in data
        print(f"✓ Parent can fetch offers. Count: {len(data['offers'])}, Enabled: {data['offers_enabled']}")

    def test_update_offer_preferences_toggle(self, parent_token):
        """Test parent can toggle offers on/off"""
        headers = {"Authorization": f"Bearer {parent_token}"}
        
        # Turn off offers
        response = requests.put(f"{BASE_URL}/api/offers/preferences", 
                               json={"offers_enabled": False}, headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify offers are disabled
        check_resp = requests.get(f"{BASE_URL}/api/offers", headers=headers)
        assert check_resp.json().get("offers_enabled") == False
        
        # Turn back on
        requests.put(f"{BASE_URL}/api/offers/preferences", 
                    json={"offers_enabled": True}, headers=headers)
        print("✓ Parent can toggle offer preferences")

    def test_dismiss_offer(self, parent_token):
        """Test parent can dismiss an offer"""
        headers = {"Authorization": f"Bearer {parent_token}"}
        
        # Get available offers
        offers_resp = requests.get(f"{BASE_URL}/api/offers", headers=headers)
        offers = offers_resp.json().get("offers", [])
        
        if offers:
            offer_id = offers[0]["id"]
            response = requests.put(f"{BASE_URL}/api/offers/preferences", 
                                   json={"dismiss_offer_id": offer_id}, headers=headers)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            print(f"✓ Parent can dismiss offer: {offer_id}")
        else:
            print("✓ Dismiss test skipped (no offers available)")

    def test_track_offer_click(self, parent_token):
        """Test offer click tracking"""
        headers = {"Authorization": f"Bearer {parent_token}"}
        
        # Get an offer to click
        offers_resp = requests.get(f"{BASE_URL}/api/offers", headers=headers)
        offers = offers_resp.json().get("offers", [])
        
        if offers:
            offer_id = offers[0]["id"]
            response = requests.post(f"{BASE_URL}/api/offers/{offer_id}/click", headers=headers)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            print(f"✓ Offer click tracked: {offer_id}")
        else:
            print("✓ Click tracking test skipped (no offers available)")


class TestAffiliateReferralRegistration:
    """Test affiliate code handling during user registration"""

    def test_register_with_affiliate_code(self):
        """Test user registration with affiliate referral code"""
        # Create an affiliate first
        aff_email = f"test_aff_reg_{uuid.uuid4().hex[:8]}@example.com"
        aff_resp = requests.post(f"{BASE_URL}/api/affiliates/signup", json={
            "email": aff_email, "full_name": "Affiliate For Reg Test"
        })
        assert aff_resp.status_code == 200
        affiliate_code = aff_resp.json()["affiliate_code"]
        
        # Register a new user with this affiliate code
        user_email = f"referred_user_{uuid.uuid4().hex[:8]}@example.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": user_email,
            "full_name": "Referred User Test",
            "password": "TestPass123!",
            "referral_code": affiliate_code
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ User registered with affiliate code: {affiliate_code}")

    def test_register_with_invalid_affiliate_code(self):
        """Test registration with invalid affiliate code still works"""
        user_email = f"invalid_ref_{uuid.uuid4().hex[:8]}@example.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": user_email,
            "full_name": "Invalid Ref User",
            "password": "TestPass123!",
            "referral_code": "AFF-INVALID123"
        })
        # Should still register successfully (invalid code is just ignored)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Registration with invalid affiliate code still succeeds")


class TestUnauthenticatedAccess:
    """Test that protected endpoints require authentication"""

    def test_admin_affiliates_requires_auth(self):
        """Test admin affiliates endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/affiliates")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Admin affiliates correctly requires auth")

    def test_brand_offers_requires_auth(self):
        """Test brand offers endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/brands/offers")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Brand offers correctly requires auth")

    def test_parent_offers_requires_auth(self):
        """Test parent offers endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/offers")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Parent offers correctly requires auth")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
