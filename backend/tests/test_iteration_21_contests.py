"""
Iteration 21: Referral Contest System Testing
Tests for:
- Admin Contest CRUD endpoints (POST, GET, PUT, DELETE)
- Public contest endpoints (GET active, GET leaderboard)
- Parent Portal: Contest banner, leaderboard, stats
"""
import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"
GUARDIAN_EMAIL = "allen@ourfamily.contact"
GUARDIAN_PASSWORD = "LexiAdmin2026!"


@pytest.fixture(scope="module")
def admin_token():
    """Login as admin and get token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def guardian_token():
    """Login as guardian and get token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": GUARDIAN_EMAIL,
        "password": GUARDIAN_PASSWORD
    })
    assert response.status_code == 200, f"Guardian login failed: {response.text}"
    return response.json()["access_token"]


class TestHealthCheck:
    """Basic health check"""
    
    def test_backend_health(self):
        """Test backend is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200


class TestAdminContestCRUD:
    """Test admin contest management endpoints"""
    
    def test_list_contests(self, admin_token):
        """GET /api/admin/contests - list all contests"""
        response = requests.get(
            f"{BASE_URL}/api/admin/contests",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Expected list of contests"
        print(f"Found {len(data)} existing contests")
    
    def test_create_contest(self, admin_token):
        """POST /api/admin/contests - create a contest"""
        start_date = datetime.utcnow().isoformat()
        end_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
        
        payload = {
            "title": "TEST_Summer Referral Race",
            "description": "Refer friends and win prizes!",
            "prize_description": "$200 Amazon Gift Card",
            "prize_value": 200.0,
            "start_date": start_date,
            "end_date": end_date,
            "is_active": True,
            "runner_up_prizes": [
                {"place": 2, "prize": "$100 Gift Card"},
                {"place": 3, "prize": "$50 Gift Card"}
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/contests",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Create contest failed: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response should have id"
        assert data["title"] == payload["title"], "Title should match"
        assert data["prize_description"] == payload["prize_description"], "Prize should match"
        assert data["is_active"] == True, "Contest should be active"
        assert len(data.get("runner_up_prizes", [])) == 2, "Should have 2 runner up prizes"
        
        # Store contest ID for other tests
        pytest.test_contest_id = data["id"]
        print(f"Created contest: {data['id']}")
    
    def test_update_contest_toggle_active(self, admin_token):
        """PUT /api/admin/contests/{id} - toggle is_active"""
        contest_id = getattr(pytest, 'test_contest_id', None)
        if not contest_id:
            pytest.skip("No test contest created")
        
        # Pause the contest
        response = requests.put(
            f"{BASE_URL}/api/admin/contests/{contest_id}",
            json={"is_active": False},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Update contest failed: {response.text}"
        
        data = response.json()
        assert data["is_active"] == False, "Contest should be paused"
        
        # Re-activate the contest
        response = requests.put(
            f"{BASE_URL}/api/admin/contests/{contest_id}",
            json={"is_active": True},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] == True, "Contest should be active again"
        print(f"Toggle test passed for contest {contest_id}")
    
    def test_verify_contest_persisted(self, admin_token):
        """GET contests and verify the created contest exists"""
        contest_id = getattr(pytest, 'test_contest_id', None)
        if not contest_id:
            pytest.skip("No test contest created")
        
        response = requests.get(
            f"{BASE_URL}/api/admin/contests",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        contests = response.json()
        found = next((c for c in contests if c["id"] == contest_id), None)
        assert found is not None, f"Contest {contest_id} should exist in list"
        assert found["title"] == "TEST_Summer Referral Race"
        print(f"Contest {contest_id} verified in list")


class TestPublicContestEndpoints:
    """Test public contest endpoints (no auth required)"""
    
    def test_get_active_contest(self):
        """GET /api/contests/active - returns active contest or empty object"""
        response = requests.get(f"{BASE_URL}/api/contests/active")
        assert response.status_code == 200
        
        data = response.json()
        # Should return either a contest object with 'id' or empty {}
        if data:
            print(f"Active contest: {data.get('title', 'N/A')}")
            assert "title" in data or data == {}, "Should have title if not empty"
        else:
            print("No active contest")
    
    def test_get_leaderboard(self):
        """GET /api/contests/leaderboard - returns leaderboard data"""
        response = requests.get(f"{BASE_URL}/api/contests/leaderboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "leaderboard" in data, "Response should have leaderboard key"
        assert isinstance(data["leaderboard"], list), "Leaderboard should be a list"
        print(f"Leaderboard has {len(data['leaderboard'])} entries")
        
        # Check leaderboard entry structure if any entries exist
        if data["leaderboard"]:
            entry = data["leaderboard"][0]
            assert "rank" in entry, "Entry should have rank"
            assert "display_name" in entry, "Entry should have display_name"
            assert "referral_count" in entry, "Entry should have referral_count"
            assert "total_earned" in entry, "Entry should have total_earned"
            print(f"Top referrer: {entry['display_name']} with {entry['referral_count']} referrals")
    
    def test_get_leaderboard_with_contest_id(self, admin_token):
        """GET /api/contests/leaderboard?contest_id=xxx - filtered by contest"""
        # Get a contest ID to test with
        response = requests.get(
            f"{BASE_URL}/api/admin/contests",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        if response.status_code == 200 and response.json():
            contest_id = response.json()[0]["id"]
            
            response = requests.get(
                f"{BASE_URL}/api/contests/leaderboard",
                params={"contest_id": contest_id}
            )
            assert response.status_code == 200
            data = response.json()
            assert "leaderboard" in data
            print(f"Leaderboard for contest {contest_id}: {len(data['leaderboard'])} entries")
        else:
            pytest.skip("No contests available for test")


class TestGuardianReferralAPI:
    """Test guardian referral-related endpoints"""
    
    def test_get_my_referral_code(self, guardian_token):
        """GET /api/referrals/my-code - get guardian's referral code"""
        response = requests.get(
            f"{BASE_URL}/api/referrals/my-code",
            headers={"Authorization": f"Bearer {guardian_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "referral_code" in data, "Should have referral_code"
        assert data["referral_code"], "Referral code should not be empty"
        print(f"Guardian referral code: {data['referral_code']}")
    
    def test_get_my_referrals(self, guardian_token):
        """GET /api/referrals/my-referrals - get guardian's referral stats"""
        response = requests.get(
            f"{BASE_URL}/api/referrals/my-referrals",
            headers={"Authorization": f"Bearer {guardian_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "referrals" in data, "Should have referrals array"
        assert "total_earned" in data, "Should have total_earned"
        assert "total_count" in data, "Should have total_count"
        print(f"Referrals: {data['total_count']}, Earned: ${data['total_earned']}")
    
    def test_get_reward_amount(self):
        """GET /api/referrals/reward-amount - get current reward amount"""
        response = requests.get(f"{BASE_URL}/api/referrals/reward-amount")
        assert response.status_code == 200
        
        data = response.json()
        assert "referral_reward_amount" in data, "Should have referral_reward_amount"
        print(f"Referral reward amount: ${data['referral_reward_amount']}")


class TestContestCleanup:
    """Cleanup test data"""
    
    def test_delete_test_contest(self, admin_token):
        """DELETE /api/admin/contests/{id} - delete test contest"""
        contest_id = getattr(pytest, 'test_contest_id', None)
        if not contest_id:
            pytest.skip("No test contest to delete")
        
        response = requests.delete(
            f"{BASE_URL}/api/admin/contests/{contest_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Delete contest failed: {response.text}"
        
        data = response.json()
        assert data.get("message") == "Contest deleted"
        print(f"Deleted test contest: {contest_id}")
    
    def test_verify_contest_deleted(self, admin_token):
        """Verify deleted contest no longer exists"""
        contest_id = getattr(pytest, 'test_contest_id', None)
        if not contest_id:
            pytest.skip("No test contest to verify")
        
        response = requests.get(
            f"{BASE_URL}/api/admin/contests",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        contests = response.json()
        found = next((c for c in contests if c["id"] == contest_id), None)
        assert found is None, f"Contest {contest_id} should not exist after deletion"
        print(f"Verified contest {contest_id} was deleted")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
