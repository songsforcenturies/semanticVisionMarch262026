"""
Iteration 23: Rebrand (Semantic Vision) + Contest Edit Feature Tests
Tests:
1. Rebrand verification (no LexiMaster in API responses)
2. Contest CRUD operations
3. Contest Edit (PUT /api/admin/contests/{id}) updates all fields
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
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get admin auth token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def admin_client(api_client, admin_token):
    """Session with admin auth header"""
    api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return api_client


# ================== HEALTH CHECK ==================
class TestHealthCheck:
    def test_backend_health(self, api_client):
        """Test backend health endpoint"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("TEST PASSED: Backend is healthy")


# ================== REBRAND TESTS ==================
class TestRebrand:
    """Verify rebrand from LexiMaster to Semantic Vision"""
    
    def test_admin_login_response_no_leximaster(self, api_client):
        """Login should not contain LexiMaster in response"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        response_text = response.text
        assert "LexiMaster" not in response_text, "LexiMaster found in login response"
        print("TEST PASSED: No 'LexiMaster' in login response")
    
    def test_guardian_login_response_no_leximaster(self, api_client):
        """Guardian login should not contain LexiMaster"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": GUARDIAN_EMAIL,
            "password": GUARDIAN_PASSWORD
        })
        assert response.status_code == 200
        response_text = response.text
        assert "LexiMaster" not in response_text, "LexiMaster found in guardian login"
        print("TEST PASSED: No 'LexiMaster' in guardian login response")


# ================== CONTEST API TESTS ==================
class TestContestList:
    """Test contest listing API"""
    
    def test_list_contests(self, admin_client):
        """Admin can list all contests"""
        response = admin_client.get(f"{BASE_URL}/api/admin/contests")
        assert response.status_code == 200
        contests = response.json()
        assert isinstance(contests, list)
        print(f"TEST PASSED: Listed {len(contests)} contests")
        return contests
    
    def test_list_contests_has_march_madness(self, admin_client):
        """Verify March Madness Referral Blitz contest exists"""
        response = admin_client.get(f"{BASE_URL}/api/admin/contests")
        assert response.status_code == 200
        contests = response.json()
        
        march_contest = None
        for c in contests:
            if "March Madness" in c.get("title", ""):
                march_contest = c
                break
        
        assert march_contest is not None, "March Madness contest not found"
        print(f"TEST PASSED: Found 'March Madness Referral Blitz' contest")
        print(f"  - Prize: {march_contest.get('prize_description')}")
        print(f"  - Active: {march_contest.get('is_active')}")
        return march_contest


class TestContestEdit:
    """Test contest edit (PUT) functionality"""
    
    @pytest.fixture(scope="class")
    def existing_contest(self, admin_client):
        """Get existing contest to test edit"""
        response = admin_client.get(f"{BASE_URL}/api/admin/contests")
        assert response.status_code == 200
        contests = response.json()
        assert len(contests) > 0, "No contests available to test edit"
        return contests[0]
    
    def test_edit_contest_title(self, admin_client, existing_contest):
        """Can update contest title"""
        contest_id = existing_contest["id"]
        original_title = existing_contest["title"]
        
        # Update title
        new_title = f"{original_title} EDITED"
        response = admin_client.put(f"{BASE_URL}/api/admin/contests/{contest_id}", json={
            "title": new_title
        })
        assert response.status_code == 200
        updated = response.json()
        assert updated["title"] == new_title
        print(f"TEST PASSED: Title updated from '{original_title}' to '{new_title}'")
        
        # Revert title
        response = admin_client.put(f"{BASE_URL}/api/admin/contests/{contest_id}", json={
            "title": original_title
        })
        assert response.status_code == 200
        print("Reverted title back to original")
    
    def test_edit_contest_prize_description(self, admin_client, existing_contest):
        """Can update contest prize_description"""
        contest_id = existing_contest["id"]
        original_prize = existing_contest.get("prize_description", "")
        
        # Update prize
        new_prize = "$500 Cash Prize"
        response = admin_client.put(f"{BASE_URL}/api/admin/contests/{contest_id}", json={
            "prize_description": new_prize
        })
        assert response.status_code == 200
        updated = response.json()
        assert updated["prize_description"] == new_prize
        print(f"TEST PASSED: Prize updated to '{new_prize}'")
        
        # Revert
        admin_client.put(f"{BASE_URL}/api/admin/contests/{contest_id}", json={
            "prize_description": original_prize
        })
        print("Reverted prize back to original")
    
    def test_edit_contest_dates(self, admin_client, existing_contest):
        """Can update contest start_date and end_date"""
        contest_id = existing_contest["id"]
        original_start = existing_contest.get("start_date")
        original_end = existing_contest.get("end_date")
        
        # New dates
        new_start = "2026-04-01T00:00:00Z"
        new_end = "2026-04-30T23:59:59Z"
        
        response = admin_client.put(f"{BASE_URL}/api/admin/contests/{contest_id}", json={
            "start_date": new_start,
            "end_date": new_end
        })
        assert response.status_code == 200
        updated = response.json()
        assert "2026-04-01" in updated["start_date"]
        assert "2026-04-30" in updated["end_date"]
        print(f"TEST PASSED: Dates updated to {new_start} - {new_end}")
        
        # Revert
        admin_client.put(f"{BASE_URL}/api/admin/contests/{contest_id}", json={
            "start_date": original_start,
            "end_date": original_end
        })
        print("Reverted dates back to original")
    
    def test_edit_contest_runner_up_prizes(self, admin_client, existing_contest):
        """Can update contest runner_up_prizes"""
        contest_id = existing_contest["id"]
        original_prizes = existing_contest.get("runner_up_prizes", [])
        
        # New runner-up prizes
        new_prizes = [
            {"place": 2, "prize": "$250 Gift Card"},
            {"place": 3, "prize": "3 Months Premium"}
        ]
        
        response = admin_client.put(f"{BASE_URL}/api/admin/contests/{contest_id}", json={
            "runner_up_prizes": new_prizes
        })
        assert response.status_code == 200
        updated = response.json()
        assert len(updated.get("runner_up_prizes", [])) == 2
        assert updated["runner_up_prizes"][0]["prize"] == "$250 Gift Card"
        print(f"TEST PASSED: Runner-up prizes updated")
        
        # Revert
        admin_client.put(f"{BASE_URL}/api/admin/contests/{contest_id}", json={
            "runner_up_prizes": original_prizes
        })
        print("Reverted runner-up prizes back to original")
    
    def test_edit_all_fields_at_once(self, admin_client, existing_contest):
        """Can update multiple fields in single request"""
        contest_id = existing_contest["id"]
        
        # Save original values
        original = {
            "title": existing_contest["title"],
            "description": existing_contest.get("description", ""),
            "prize_description": existing_contest.get("prize_description", ""),
            "prize_value": existing_contest.get("prize_value"),
            "start_date": existing_contest.get("start_date"),
            "end_date": existing_contest.get("end_date"),
            "runner_up_prizes": existing_contest.get("runner_up_prizes", [])
        }
        
        # Update all fields
        update_data = {
            "title": "TEST: Full Edit Contest",
            "description": "Testing full edit capability",
            "prize_description": "$1000 Grand Prize",
            "prize_value": 1000.0,
            "start_date": "2026-05-01T00:00:00Z",
            "end_date": "2026-05-31T23:59:59Z",
            "runner_up_prizes": [
                {"place": 2, "prize": "$500"},
                {"place": 3, "prize": "$250"}
            ]
        }
        
        response = admin_client.put(f"{BASE_URL}/api/admin/contests/{contest_id}", json=update_data)
        assert response.status_code == 200
        updated = response.json()
        
        # Verify all fields updated
        assert updated["title"] == "TEST: Full Edit Contest"
        assert updated["description"] == "Testing full edit capability"
        assert updated["prize_description"] == "$1000 Grand Prize"
        assert updated["prize_value"] == 1000.0
        assert "2026-05-01" in updated["start_date"]
        assert "2026-05-31" in updated["end_date"]
        assert len(updated["runner_up_prizes"]) == 2
        
        print("TEST PASSED: All fields updated in single request")
        print(f"  - title: {updated['title']}")
        print(f"  - description: {updated['description']}")
        print(f"  - prize_description: {updated['prize_description']}")
        print(f"  - prize_value: {updated['prize_value']}")
        print(f"  - start_date: {updated['start_date']}")
        print(f"  - end_date: {updated['end_date']}")
        print(f"  - runner_up_prizes: {updated['runner_up_prizes']}")
        
        # Revert to original
        response = admin_client.put(f"{BASE_URL}/api/admin/contests/{contest_id}", json=original)
        assert response.status_code == 200
        print("Reverted all fields back to original")
    
    def test_edit_nonexistent_contest_returns_404(self, admin_client):
        """Editing non-existent contest returns 404"""
        fake_id = "nonexistent-contest-id-12345"
        response = admin_client.put(f"{BASE_URL}/api/admin/contests/{fake_id}", json={
            "title": "Should Fail"
        })
        assert response.status_code == 404
        print("TEST PASSED: 404 returned for non-existent contest edit")
    
    def test_edit_empty_data_returns_400(self, admin_client, existing_contest):
        """Editing with empty data returns 400"""
        contest_id = existing_contest["id"]
        response = admin_client.put(f"{BASE_URL}/api/admin/contests/{contest_id}", json={})
        assert response.status_code == 400
        print("TEST PASSED: 400 returned for empty edit data")


class TestContestToggle:
    """Test contest activate/pause (is_active toggle)"""
    
    def test_toggle_contest_active_status(self, admin_client):
        """Can toggle contest is_active status"""
        # Get contests
        response = admin_client.get(f"{BASE_URL}/api/admin/contests")
        assert response.status_code == 200
        contests = response.json()
        assert len(contests) > 0
        
        contest = contests[0]
        contest_id = contest["id"]
        original_active = contest.get("is_active", True)
        
        # Toggle to opposite
        new_active = not original_active
        response = admin_client.put(f"{BASE_URL}/api/admin/contests/{contest_id}", json={
            "is_active": new_active
        })
        assert response.status_code == 200
        updated = response.json()
        assert updated["is_active"] == new_active
        print(f"TEST PASSED: is_active toggled from {original_active} to {new_active}")
        
        # Revert
        admin_client.put(f"{BASE_URL}/api/admin/contests/{contest_id}", json={
            "is_active": original_active
        })
        print("Reverted is_active back to original")


class TestPublicContestEndpoints:
    """Test public contest endpoints (no auth required)"""
    
    def test_get_active_contest_public(self, api_client):
        """Public endpoint returns active contest"""
        response = api_client.get(f"{BASE_URL}/api/contests/active")
        assert response.status_code == 200
        # Can be empty object if no active contest, or contest data
        data = response.json()
        print(f"TEST PASSED: /contests/active returned: {type(data)}")
        if data:
            print(f"  - Active contest: {data.get('title', 'N/A')}")
    
    def test_get_leaderboard_public(self, api_client):
        """Public leaderboard endpoint works"""
        response = api_client.get(f"{BASE_URL}/api/contests/leaderboard")
        assert response.status_code == 200
        data = response.json()
        # API returns {"leaderboard": [...]} format
        assert "leaderboard" in data or isinstance(data, list)
        leaderboard = data.get("leaderboard", data) if isinstance(data, dict) else data
        print(f"TEST PASSED: /contests/leaderboard returned {len(leaderboard)} entries")


# ================== CONTEST CREATE & DELETE TESTS ==================
class TestContestCreateDelete:
    """Test contest creation and deletion"""
    
    def test_create_and_delete_contest(self, admin_client):
        """Create a new contest and then delete it"""
        # Create
        create_data = {
            "title": "TEST_Contest_For_Deletion",
            "description": "This contest will be deleted",
            "prize_description": "$50 Test Prize",
            "prize_value": 50.0,
            "start_date": "2026-06-01T00:00:00Z",
            "end_date": "2026-06-30T23:59:59Z",
            "is_active": False,
            "runner_up_prizes": [{"place": 2, "prize": "$25"}]
        }
        
        response = admin_client.post(f"{BASE_URL}/api/admin/contests", json=create_data)
        assert response.status_code == 200
        created = response.json()
        contest_id = created["id"]
        assert created["title"] == "TEST_Contest_For_Deletion"
        print(f"TEST PASSED: Created contest with id {contest_id}")
        
        # Verify it's in the list
        response = admin_client.get(f"{BASE_URL}/api/admin/contests")
        contests = response.json()
        found = any(c["id"] == contest_id for c in contests)
        assert found, "Created contest not found in list"
        print("TEST PASSED: Created contest found in list")
        
        # Delete
        response = admin_client.delete(f"{BASE_URL}/api/admin/contests/{contest_id}")
        assert response.status_code == 200
        print(f"TEST PASSED: Deleted contest {contest_id}")
        
        # Verify it's gone
        response = admin_client.get(f"{BASE_URL}/api/admin/contests")
        contests = response.json()
        found = any(c["id"] == contest_id for c in contests)
        assert not found, "Deleted contest still in list"
        print("TEST PASSED: Deleted contest no longer in list")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
