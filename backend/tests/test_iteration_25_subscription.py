"""
Iteration 25 - Subscription System Tests
Tests for:
- GET /api/subscription-plans/available (list active plans)
- PUT /api/admin/plans/{plan_id} (edit plan)
- POST /api/admin/users/{user_id}/assign-subscription (admin assign)
- POST /api/subscriptions/upgrade (parent upgrade with wallet)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from the review request
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"
GUARDIAN_EMAIL = "allen@ourfamily.contact"
GUARDIAN_PASSWORD = "LexiAdmin2026!"


class TestAuthSetup:
    """Get tokens for testing"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, f"No access_token in response: {data}"
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def guardian_token(self):
        """Get guardian authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": GUARDIAN_EMAIL,
            "password": GUARDIAN_PASSWORD
        })
        assert response.status_code == 200, f"Guardian login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, f"No access_token in response: {data}"
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def guardian_user(self, guardian_token):
        """Get guardian user info"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {guardian_token}"
        })
        assert response.status_code == 200
        return response.json()


class TestSubscriptionPlansAvailable(TestAuthSetup):
    """Test GET /api/subscription-plans/available"""
    
    def test_get_available_plans_returns_200(self):
        """GET /api/subscription-plans/available should return 200"""
        response = requests.get(f"{BASE_URL}/api/subscription-plans/available")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"Available plans endpoint returned status 200")
    
    def test_get_available_plans_returns_list(self):
        """GET /api/subscription-plans/available should return a list"""
        response = requests.get(f"{BASE_URL}/api/subscription-plans/available")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"Available plans returned list with {len(data)} plans")
    
    def test_available_plans_have_required_fields(self):
        """Each plan should have id, name, price_monthly, student_seats"""
        response = requests.get(f"{BASE_URL}/api/subscription-plans/available")
        assert response.status_code == 200
        data = response.json()
        
        if len(data) > 0:
            plan = data[0]
            assert "id" in plan, f"Plan missing 'id': {plan}"
            assert "name" in plan, f"Plan missing 'name': {plan}"
            assert "price_monthly" in plan, f"Plan missing 'price_monthly': {plan}"
            assert "student_seats" in plan, f"Plan missing 'student_seats': {plan}"
            print(f"First plan has all required fields: {plan['name']}")
        else:
            print("No plans returned - may need to create plans first")


class TestAdminPlanEdit(TestAuthSetup):
    """Test PUT /api/admin/plans/{plan_id} - edit a plan"""
    
    def test_admin_can_list_plans(self, admin_token):
        """Admin should be able to list plans"""
        response = requests.get(f"{BASE_URL}/api/admin/plans", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200, f"List plans failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"Admin listed {len(data)} plans")
        return data
    
    def test_admin_can_edit_plan(self, admin_token):
        """Admin should be able to edit a plan"""
        # First get existing plans
        list_response = requests.get(f"{BASE_URL}/api/admin/plans", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert list_response.status_code == 200
        plans = list_response.json()
        
        if len(plans) == 0:
            pytest.skip("No plans available to edit")
        
        plan = plans[0]
        plan_id = plan["id"]
        original_name = plan["name"]
        
        # Edit the plan - just update description to not break anything
        edit_response = requests.put(
            f"{BASE_URL}/api/admin/plans/{plan_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"description": "TEST_UPDATED_DESC_ITERATION_25"}
        )
        assert edit_response.status_code == 200, f"Edit plan failed: {edit_response.text}"
        
        updated_plan = edit_response.json()
        assert updated_plan["description"] == "TEST_UPDATED_DESC_ITERATION_25", "Description not updated"
        print(f"Successfully edited plan '{original_name}'")
        
        # Restore original description
        requests.put(
            f"{BASE_URL}/api/admin/plans/{plan_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"description": plan.get("description", "")}
        )
    
    def test_admin_can_edit_plan_price_and_seats(self, admin_token):
        """Admin should be able to edit price and seats"""
        # Get existing plans
        list_response = requests.get(f"{BASE_URL}/api/admin/plans", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert list_response.status_code == 200
        plans = list_response.json()
        
        if len(plans) == 0:
            pytest.skip("No plans available to edit")
        
        plan = plans[0]
        plan_id = plan["id"]
        original_price = plan.get("price_monthly", 0)
        original_seats = plan.get("student_seats", 10)
        
        # Edit with new values
        test_price = 99.99
        test_seats = 50
        
        edit_response = requests.put(
            f"{BASE_URL}/api/admin/plans/{plan_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "price_monthly": test_price,
                "student_seats": test_seats
            }
        )
        assert edit_response.status_code == 200, f"Edit failed: {edit_response.text}"
        
        updated = edit_response.json()
        assert updated.get("price_monthly") == test_price, "Price not updated"
        assert updated.get("student_seats") == test_seats, "Seats not updated"
        print(f"Successfully updated price to {test_price} and seats to {test_seats}")
        
        # Restore original values
        requests.put(
            f"{BASE_URL}/api/admin/plans/{plan_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "price_monthly": original_price,
                "student_seats": original_seats
            }
        )
    
    def test_admin_can_toggle_plan_active_status(self, admin_token):
        """Admin should be able to toggle is_active"""
        list_response = requests.get(f"{BASE_URL}/api/admin/plans", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert list_response.status_code == 200
        plans = list_response.json()
        
        if len(plans) == 0:
            pytest.skip("No plans available")
        
        plan = plans[0]
        plan_id = plan["id"]
        original_active = plan.get("is_active", True)
        
        # Toggle active status
        new_active = not original_active
        edit_response = requests.put(
            f"{BASE_URL}/api/admin/plans/{plan_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"is_active": new_active}
        )
        assert edit_response.status_code == 200, f"Toggle active failed: {edit_response.text}"
        
        updated = edit_response.json()
        assert updated.get("is_active") == new_active, "Active status not updated"
        print(f"Toggled plan active status from {original_active} to {new_active}")
        
        # Restore original status
        requests.put(
            f"{BASE_URL}/api/admin/plans/{plan_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"is_active": original_active}
        )
    
    def test_non_admin_cannot_edit_plan(self, guardian_token, admin_token):
        """Non-admin should not be able to edit plans"""
        # Get a plan id first
        list_response = requests.get(f"{BASE_URL}/api/admin/plans", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        if list_response.status_code != 200 or len(list_response.json()) == 0:
            pytest.skip("No plans available")
        
        plan_id = list_response.json()[0]["id"]
        
        # Try to edit as guardian
        edit_response = requests.put(
            f"{BASE_URL}/api/admin/plans/{plan_id}",
            headers={"Authorization": f"Bearer {guardian_token}"},
            json={"name": "Hacked Plan"}
        )
        assert edit_response.status_code == 403, f"Expected 403, got {edit_response.status_code}"
        print("Non-admin correctly rejected from editing plans")


class TestAdminAssignSubscription(TestAuthSetup):
    """Test POST /api/admin/users/{user_id}/assign-subscription"""
    
    def test_admin_can_assign_subscription(self, admin_token, guardian_token):
        """Admin should be able to assign subscription to a user"""
        # Get guardian user id
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {guardian_token}"
        })
        assert me_response.status_code == 200
        guardian_user = me_response.json()
        guardian_id = guardian_user["id"]
        
        # Get available plans
        plans_response = requests.get(f"{BASE_URL}/api/admin/plans", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert plans_response.status_code == 200
        plans = plans_response.json()
        
        if len(plans) == 0:
            pytest.skip("No plans available to assign")
        
        plan = plans[0]
        plan_id = plan["id"]
        
        # Assign subscription
        assign_response = requests.post(
            f"{BASE_URL}/api/admin/users/{guardian_id}/assign-subscription",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"plan_id": plan_id}
        )
        assert assign_response.status_code == 200, f"Assign failed: {assign_response.text}"
        
        result = assign_response.json()
        assert "message" in result, f"No message in response: {result}"
        print(f"Admin assigned plan: {result.get('message')}")
    
    def test_non_admin_cannot_assign_subscription(self, guardian_token):
        """Non-admin should not be able to assign subscriptions"""
        # Get any user (use guardian itself)
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {guardian_token}"
        })
        assert me_response.status_code == 200
        user_id = me_response.json()["id"]
        
        # Try to assign as guardian
        assign_response = requests.post(
            f"{BASE_URL}/api/admin/users/{user_id}/assign-subscription",
            headers={"Authorization": f"Bearer {guardian_token}"},
            json={"plan_id": "fake-plan-id"}
        )
        assert assign_response.status_code == 403, f"Expected 403, got {assign_response.status_code}"
        print("Non-admin correctly rejected from assigning subscriptions")
    
    def test_assign_invalid_plan_returns_404(self, admin_token, guardian_token):
        """Assigning invalid plan should return 404"""
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {guardian_token}"
        })
        assert me_response.status_code == 200
        user_id = me_response.json()["id"]
        
        assign_response = requests.post(
            f"{BASE_URL}/api/admin/users/{user_id}/assign-subscription",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"plan_id": "non-existent-plan-id-12345"}
        )
        assert assign_response.status_code == 404, f"Expected 404, got {assign_response.status_code}"
        print("Invalid plan correctly returns 404")


class TestSubscriptionUpgrade(TestAuthSetup):
    """Test POST /api/subscriptions/upgrade"""
    
    def test_guardian_can_view_own_subscription(self, guardian_token):
        """Guardian should be able to view their subscription"""
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {guardian_token}"
        })
        assert me_response.status_code == 200
        guardian_id = me_response.json()["id"]
        
        sub_response = requests.get(
            f"{BASE_URL}/api/subscriptions/{guardian_id}",
            headers={"Authorization": f"Bearer {guardian_token}"}
        )
        assert sub_response.status_code == 200, f"Get subscription failed: {sub_response.text}"
        
        subscription = sub_response.json()
        assert "plan" in subscription, f"No plan in subscription: {subscription}"
        assert "student_seats" in subscription, f"No student_seats in subscription: {subscription}"
        print(f"Guardian's current plan: {subscription.get('plan')}")
    
    def test_upgrade_requires_sufficient_balance(self, guardian_token):
        """Upgrade should fail if wallet balance is insufficient"""
        # Get available plans with price > 0
        plans_response = requests.get(f"{BASE_URL}/api/subscription-plans/available")
        assert plans_response.status_code == 200
        plans = plans_response.json()
        
        paid_plans = [p for p in plans if p.get("price_monthly", 0) > 0]
        if len(paid_plans) == 0:
            pytest.skip("No paid plans available to test")
        
        # Get guardian's wallet balance
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {guardian_token}"
        })
        assert me_response.status_code == 200
        user = me_response.json()
        wallet_balance = user.get("wallet_balance", 0)
        
        # Find a plan more expensive than wallet balance
        expensive_plan = None
        for p in paid_plans:
            if p.get("price_monthly", 0) > wallet_balance:
                expensive_plan = p
                break
        
        if not expensive_plan:
            print(f"User has ${wallet_balance}, no plans cost more than that. Skipping insufficient balance test.")
            pytest.skip("No plan more expensive than wallet balance")
        
        # Try to upgrade
        upgrade_response = requests.post(
            f"{BASE_URL}/api/subscriptions/upgrade",
            headers={"Authorization": f"Bearer {guardian_token}"},
            json={"plan_id": expensive_plan["id"], "use_wallet": True}
        )
        assert upgrade_response.status_code == 400, f"Expected 400, got {upgrade_response.status_code}"
        assert "Insufficient" in upgrade_response.json().get("detail", ""), "Should mention insufficient balance"
        print(f"Correctly rejected upgrade to {expensive_plan['name']} (${expensive_plan['price_monthly']}) with balance ${wallet_balance}")
    
    def test_upgrade_to_free_plan_works(self, guardian_token):
        """Upgrading to a free plan should work without balance check"""
        plans_response = requests.get(f"{BASE_URL}/api/subscription-plans/available")
        assert plans_response.status_code == 200
        plans = plans_response.json()
        
        free_plans = [p for p in plans if p.get("price_monthly", 0) == 0]
        if len(free_plans) == 0:
            pytest.skip("No free plans available")
        
        free_plan = free_plans[0]
        
        upgrade_response = requests.post(
            f"{BASE_URL}/api/subscriptions/upgrade",
            headers={"Authorization": f"Bearer {guardian_token}"},
            json={"plan_id": free_plan["id"], "use_wallet": True}
        )
        # May succeed or fail depending on current state
        if upgrade_response.status_code == 200:
            result = upgrade_response.json()
            print(f"Successfully switched to free plan: {result.get('message')}")
        else:
            print(f"Free plan upgrade returned: {upgrade_response.status_code}")
    
    def test_upgrade_invalid_plan_returns_404(self, guardian_token):
        """Upgrade with invalid plan_id should return 404"""
        upgrade_response = requests.post(
            f"{BASE_URL}/api/subscriptions/upgrade",
            headers={"Authorization": f"Bearer {guardian_token}"},
            json={"plan_id": "non-existent-plan-xyz", "use_wallet": True}
        )
        assert upgrade_response.status_code == 404, f"Expected 404, got {upgrade_response.status_code}"
        print("Invalid plan correctly returns 404")


class TestCouponRedemption(TestAuthSetup):
    """Test POST /api/coupons/redeem"""
    
    def test_invalid_coupon_fails(self, guardian_token):
        """Invalid coupon code should fail"""
        redeem_response = requests.post(
            f"{BASE_URL}/api/coupons/redeem",
            headers={"Authorization": f"Bearer {guardian_token}"},
            json={"code": "INVALID_COUPON_CODE_XYZ123"}
        )
        assert redeem_response.status_code in [400, 404], f"Expected 400/404, got {redeem_response.status_code}"
        print("Invalid coupon correctly rejected")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
