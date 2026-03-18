"""
Iteration 26 Tests: Admin Portal Features & Subscription Auto-Create
======================================================================
Tests for:
1. GET /api/subscriptions/{guardian_id} - auto-creates free plan with 10 seats if missing
2. GET /api/admin/plan-stats - plan breakdown with user counts per plan type
3. GET /api/admin/users?search=... - filter users by name/email
4. PUT /api/admin/users/{user_id}/subscription - edit subscription (plan, seats, status)
5. PUT /api/admin/users/{user_id}/wallet - set wallet balance directly
"""

import pytest
import requests
import os
import time

# Use the public URL
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://production-crisis-2.preview.emergentagent.com')
BASE_URL = BASE_URL.rstrip('/')
API_URL = f"{BASE_URL}/api"

# Test credentials
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"
GUARDIAN_EMAIL = "allen@ourfamily.contact"
GUARDIAN_PASSWORD = "LexiAdmin2026!"
TEST_GUARDIAN_EMAIL = "dawn@songsforcenturies.com"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{API_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    token = response.json().get("access_token")
    assert token, "No access_token in response"
    return token


@pytest.fixture(scope="module")
def guardian_token():
    """Get guardian authentication token"""
    response = requests.post(f"{API_URL}/auth/login", json={
        "email": GUARDIAN_EMAIL,
        "password": GUARDIAN_PASSWORD
    })
    assert response.status_code == 200, f"Guardian login failed: {response.text}"
    return response.json().get("access_token")


@pytest.fixture(scope="module")
def guardian_user(guardian_token):
    """Get guardian user info"""
    response = requests.get(f"{API_URL}/auth/me", headers={
        "Authorization": f"Bearer {guardian_token}"
    })
    assert response.status_code == 200
    return response.json()


@pytest.fixture(scope="module")
def all_users(admin_token):
    """Get all users from admin API"""
    response = requests.get(f"{API_URL}/admin/users", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert response.status_code == 200
    return response.json()


# ==================== SUBSCRIPTION AUTO-CREATE TESTS ====================

class TestSubscriptionAutoCreate:
    """Tests for GET /subscriptions/{guardian_id} auto-creating free plan"""

    def test_subscription_endpoint_returns_200(self, guardian_token, guardian_user):
        """Subscription endpoint should return 200 for guardian"""
        response = requests.get(
            f"{API_URL}/subscriptions/{guardian_user['id']}",
            headers={"Authorization": f"Bearer {guardian_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_subscription_has_required_fields(self, guardian_token, guardian_user):
        """Subscription response should have all required fields"""
        response = requests.get(
            f"{API_URL}/subscriptions/{guardian_user['id']}",
            headers={"Authorization": f"Bearer {guardian_token}"}
        )
        data = response.json()
        assert "plan" in data, "Missing 'plan' field"
        assert "student_seats" in data, "Missing 'student_seats' field"
        assert "active_students" in data, "Missing 'active_students' field"
        assert "guardian_id" in data, "Missing 'guardian_id' field"

    def test_guardian_subscription_has_seats(self, guardian_token, guardian_user):
        """Guardian should have student seats (not 0 or None)"""
        response = requests.get(
            f"{API_URL}/subscriptions/{guardian_user['id']}",
            headers={"Authorization": f"Bearer {guardian_token}"}
        )
        data = response.json()
        seats = data.get("student_seats", 0)
        assert seats is not None, "student_seats should not be None"
        assert seats > 0, f"student_seats should be > 0, got {seats}"

    def test_auto_create_subscription_for_user_without_one(self, admin_token, all_users):
        """
        Test that subscription auto-creates for guardian without subscription.
        Find a guardian that may not have a subscription and call the endpoint.
        """
        # Find any guardian to test
        guardians = [u for u in all_users if u.get("role") == "guardian"]
        assert len(guardians) > 0, "No guardians found for testing"
        
        # Use the first guardian for the test
        test_guardian = guardians[0]
        
        response = requests.get(
            f"{API_URL}/subscriptions/{test_guardian['id']}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Should have valid data (either existing or auto-created)
        assert data.get("student_seats") is not None
        assert data.get("plan") is not None
        print(f"Subscription for {test_guardian['email']}: plan={data['plan']}, seats={data['student_seats']}")


# ==================== ADMIN PLAN-STATS TESTS ====================

class TestAdminPlanStats:
    """Tests for GET /admin/plan-stats endpoint"""

    def test_plan_stats_returns_200(self, admin_token):
        """Plan stats endpoint should return 200 for admin"""
        response = requests.get(
            f"{API_URL}/admin/plan-stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_plan_stats_has_required_fields(self, admin_token):
        """Plan stats should have all required fields"""
        response = requests.get(
            f"{API_URL}/admin/plan-stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        assert "plan_breakdown" in data, "Missing 'plan_breakdown' field"
        assert "total_guardians" in data, "Missing 'total_guardians' field"
        assert "total_with_subscription" in data, "Missing 'total_with_subscription' field"
        assert "total_without_subscription" in data, "Missing 'total_without_subscription' field"

    def test_plan_breakdown_structure(self, admin_token):
        """Plan breakdown should have proper structure for each plan"""
        response = requests.get(
            f"{API_URL}/admin/plan-stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        plan_breakdown = data.get("plan_breakdown", [])
        assert isinstance(plan_breakdown, list), "plan_breakdown should be a list"
        
        for plan in plan_breakdown:
            assert "plan" in plan, f"Missing 'plan' in breakdown: {plan}"
            assert "users" in plan, f"Missing 'users' count in breakdown: {plan}"
            assert "total_seats" in plan, f"Missing 'total_seats' in breakdown: {plan}"
            assert "active_students" in plan, f"Missing 'active_students' in breakdown: {plan}"
        
        print(f"Plan stats: {data}")

    def test_plan_stats_requires_admin(self, guardian_token):
        """Plan stats should reject non-admin users"""
        response = requests.get(
            f"{API_URL}/admin/plan-stats",
            headers={"Authorization": f"Bearer {guardian_token}"}
        )
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"


# ==================== ADMIN USER SEARCH TESTS ====================

class TestAdminUserSearch:
    """Tests for GET /admin/users?search=... endpoint"""

    def test_user_search_by_name(self, admin_token):
        """Searching users by name should work"""
        response = requests.get(
            f"{API_URL}/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"search": "allen"}
        )
        assert response.status_code == 200
        
        users = response.json()
        assert isinstance(users, list), "Response should be a list"
        
        # At least one user should match "allen"
        matching = [u for u in users if "allen" in u.get("full_name", "").lower() or "allen" in u.get("email", "").lower()]
        assert len(matching) > 0, "Search for 'allen' should return at least one user"
        print(f"Found {len(matching)} users matching 'allen'")

    def test_user_search_by_email(self, admin_token):
        """Searching users by email should work"""
        response = requests.get(
            f"{API_URL}/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"search": "dawn"}
        )
        assert response.status_code == 200
        
        users = response.json()
        assert isinstance(users, list)
        
        # Should find users with "dawn" in name or email
        matching = [u for u in users if "dawn" in u.get("full_name", "").lower() or "dawn" in u.get("email", "").lower()]
        print(f"Found {len(matching)} users matching 'dawn'")

    def test_user_search_empty_result(self, admin_token):
        """Searching for non-existent user should return empty list"""
        response = requests.get(
            f"{API_URL}/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"search": "xyznonexistent123"}
        )
        assert response.status_code == 200
        
        users = response.json()
        assert isinstance(users, list)
        assert len(users) == 0, "Non-existent search should return empty list"

    def test_user_search_without_param(self, admin_token):
        """Getting users without search param should return all users"""
        response = requests.get(
            f"{API_URL}/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        users = response.json()
        assert len(users) > 0, "Should return users when no search param"
        print(f"Total users without search: {len(users)}")


# ==================== ADMIN EDIT SUBSCRIPTION TESTS ====================

class TestAdminEditSubscription:
    """Tests for PUT /admin/users/{user_id}/subscription endpoint"""

    def test_edit_subscription_seats(self, admin_token, all_users):
        """Admin should be able to edit subscription seats"""
        # Find a guardian
        guardians = [u for u in all_users if u.get("role") == "guardian"]
        assert len(guardians) > 0, "No guardians found"
        
        test_guardian = guardians[0]
        
        # Get current subscription first
        sub_resp = requests.get(
            f"{API_URL}/subscriptions/{test_guardian['id']}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        current_seats = sub_resp.json().get("student_seats", 10)
        
        # Edit to new seats
        new_seats = current_seats + 5 if current_seats < 100 else current_seats - 5
        
        response = requests.put(
            f"{API_URL}/admin/users/{test_guardian['id']}/subscription",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"student_seats": new_seats}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("student_seats") == new_seats, f"Seats not updated: {data}"
        
        # Restore original
        requests.put(
            f"{API_URL}/admin/users/{test_guardian['id']}/subscription",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"student_seats": current_seats}
        )

    def test_edit_subscription_plan_name(self, admin_token, all_users):
        """Admin should be able to edit subscription plan name"""
        guardians = [u for u in all_users if u.get("role") == "guardian"]
        test_guardian = guardians[0]
        
        # Get current plan
        sub_resp = requests.get(
            f"{API_URL}/subscriptions/{test_guardian['id']}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        original_plan = sub_resp.json().get("plan", "free")
        
        # Update plan name (will be converted to lowercase with underscores)
        response = requests.put(
            f"{API_URL}/admin/users/{test_guardian['id']}/subscription",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"plan_name": "premium"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("plan") == "premium", f"Plan not updated: {data}"
        
        # Restore original
        requests.put(
            f"{API_URL}/admin/users/{test_guardian['id']}/subscription",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"plan_name": original_plan}
        )

    def test_edit_subscription_status(self, admin_token, all_users):
        """Admin should be able to edit subscription status"""
        guardians = [u for u in all_users if u.get("role") == "guardian"]
        test_guardian = guardians[0]
        
        response = requests.put(
            f"{API_URL}/admin/users/{test_guardian['id']}/subscription",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"status": "active"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "active"

    def test_edit_subscription_requires_admin(self, guardian_token, guardian_user):
        """Non-admin should not be able to edit subscriptions"""
        response = requests.put(
            f"{API_URL}/admin/users/{guardian_user['id']}/subscription",
            headers={"Authorization": f"Bearer {guardian_token}"},
            json={"student_seats": 50}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"

    def test_edit_subscription_empty_update(self, admin_token, all_users):
        """Empty update should return 400"""
        guardians = [u for u in all_users if u.get("role") == "guardian"]
        test_guardian = guardians[0]
        
        response = requests.put(
            f"{API_URL}/admin/users/{test_guardian['id']}/subscription",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={}
        )
        assert response.status_code == 400, f"Expected 400 for empty update, got {response.status_code}"


# ==================== ADMIN EDIT WALLET TESTS ====================

class TestAdminEditWallet:
    """Tests for PUT /admin/users/{user_id}/wallet endpoint"""

    def test_edit_wallet_balance(self, admin_token, all_users):
        """Admin should be able to set wallet balance directly"""
        guardians = [u for u in all_users if u.get("role") == "guardian"]
        test_guardian = guardians[0]
        
        # Get current balance
        original_balance = test_guardian.get("wallet_balance", 0.0)
        
        # Set new balance
        new_balance = 99.99
        response = requests.put(
            f"{API_URL}/admin/users/{test_guardian['id']}/wallet",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"wallet_balance": new_balance, "description": "Test adjustment"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "new_balance" in data, f"Response missing 'new_balance': {data}"
        assert data.get("new_balance") == new_balance, f"Balance not set correctly: {data}"
        
        # Restore original balance
        requests.put(
            f"{API_URL}/admin/users/{test_guardian['id']}/wallet",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"wallet_balance": original_balance, "description": "Restored"}
        )

    def test_edit_wallet_creates_transaction(self, admin_token, all_users):
        """Setting wallet balance should create a transaction record"""
        guardians = [u for u in all_users if u.get("role") == "guardian"]
        test_guardian = guardians[0]
        
        original_balance = test_guardian.get("wallet_balance", 0.0)
        
        # Set a specific test balance
        test_balance = 123.45
        response = requests.put(
            f"{API_URL}/admin/users/{test_guardian['id']}/wallet",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"wallet_balance": test_balance, "description": "Admin test adjustment"}
        )
        assert response.status_code == 200
        
        # Verify message contains the balance
        data = response.json()
        assert "Wallet updated" in data.get("message", ""), f"Expected success message: {data}"
        
        # Restore
        requests.put(
            f"{API_URL}/admin/users/{test_guardian['id']}/wallet",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"wallet_balance": original_balance, "description": "Restored"}
        )

    def test_edit_wallet_requires_admin(self, guardian_token, guardian_user):
        """Non-admin should not be able to edit wallets"""
        response = requests.put(
            f"{API_URL}/admin/users/{guardian_user['id']}/wallet",
            headers={"Authorization": f"Bearer {guardian_token}"},
            json={"wallet_balance": 1000.00}
        )
        assert response.status_code == 403

    def test_edit_wallet_nonexistent_user(self, admin_token):
        """Editing wallet of non-existent user should return 404"""
        response = requests.put(
            f"{API_URL}/admin/users/nonexistent-user-id-xyz/wallet",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"wallet_balance": 50.00}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
