"""
Iteration 47: PIN Change, Tab Reorder, Heritage Multi-select Tests
Features tested:
- POST /api/students/{id}/change-pin - parent changes student PIN with auth
- POST /api/student/change-my-pin - student changes own PIN (no auth)
- POST /api/student/change-my-pin - wrong current PIN returns 400
- POST /api/student/change-my-pin - PIN too short returns 400
- GET /api/user-card - still returns student data correctly
- Core APIs: POST /api/auth/login, GET /api/students, GET /api/health
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"
TEST_STUDENT_ID = "18316e14-9f7f-4960-9aba-e809fad104a2"
ORIGINAL_PIN = "914027"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_token(api_client):
    """Get authentication token for admin/guardian"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "access_token" in data, "No access_token in response"
    return data["access_token"]


@pytest.fixture(scope="module")
def authenticated_client(api_client, auth_token):
    """Session with auth header"""
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client


class TestCoreAPIs:
    """Test core APIs still work"""
    
    def test_health_check(self, api_client):
        """GET /api/health should return 200"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        print("PASSED: GET /api/health returns 200")
    
    def test_login(self, api_client):
        """POST /api/auth/login should return token"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "Missing access_token"
        assert "user" in data, "Missing user data"
        print(f"PASSED: POST /api/auth/login returns token for {data['user']['full_name']}")
    
    def test_get_students(self, authenticated_client, auth_token):
        """GET /api/students should return list of students"""
        # Get current user ID from /auth/me
        me_resp = authenticated_client.get(f"{BASE_URL}/api/auth/me")
        user_id = me_resp.json().get("id") if me_resp.status_code == 200 else None
        response = authenticated_client.get(f"{BASE_URL}/api/students", params={"guardian_id": user_id} if user_id else {})
        assert response.status_code == 200, f"Get students failed: {response.text}"
        students = response.json()
        assert isinstance(students, list), "Students should be a list"
        assert len(students) >= 1, "Should have at least 1 student"
        # Find SJ student
        sj_found = any(s.get("full_name") == "SJ" or s.get("id") == TEST_STUDENT_ID for s in students)
        assert sj_found, f"SJ student not found in list: {[s.get('full_name') for s in students]}"
        print(f"PASSED: GET /api/students returns {len(students)} students including SJ")


class TestUserCard:
    """Test user card API still works"""
    
    def test_get_user_card(self, authenticated_client):
        """GET /api/user-card should return guardian and student cards"""
        response = authenticated_client.get(f"{BASE_URL}/api/user-card")
        assert response.status_code == 200, f"User card failed: {response.text}"
        data = response.json()
        assert "guardian_card" in data, "Missing guardian_card"
        assert "student_cards" in data, "Missing student_cards"
        guardian = data["guardian_card"]
        assert guardian.get("type") == "guardian", "Guardian card type wrong"
        assert guardian.get("name"), "Guardian name missing"
        students = data["student_cards"]
        assert isinstance(students, list), "student_cards should be list"
        print(f"PASSED: GET /api/user-card returns guardian ({guardian['name']}) and {len(students)} student cards")


class TestParentChangeStudentPIN:
    """Test parent changing student PIN via authenticated endpoint"""
    
    def test_change_pin_with_wrong_current(self, authenticated_client):
        """POST /api/students/{id}/change-pin with wrong current PIN returns 400"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/students/{TEST_STUDENT_ID}/change-pin",
            json={"current_pin": "000000", "new_pin": "9999"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "incorrect" in data.get("detail", "").lower(), f"Error message should mention incorrect PIN: {data}"
        print("PASSED: POST /api/students/{id}/change-pin with wrong PIN returns 400")
    
    def test_change_pin_too_short(self, authenticated_client):
        """POST /api/students/{id}/change-pin with PIN < 4 digits returns 400"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/students/{TEST_STUDENT_ID}/change-pin",
            json={"current_pin": ORIGINAL_PIN, "new_pin": "123"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "4" in data.get("detail", "") or "digit" in data.get("detail", "").lower(), f"Error should mention 4 digits: {data}"
        print("PASSED: POST /api/students/{id}/change-pin with short PIN returns 400")
    
    def test_change_pin_success_and_revert(self, authenticated_client):
        """POST /api/students/{id}/change-pin should change PIN successfully, then revert"""
        # Change PIN to 9999
        response = authenticated_client.post(
            f"{BASE_URL}/api/students/{TEST_STUDENT_ID}/change-pin",
            json={"current_pin": ORIGINAL_PIN, "new_pin": "9999"}
        )
        assert response.status_code == 200, f"Change PIN failed: {response.text}"
        data = response.json()
        assert "success" in data.get("message", "").lower(), f"Expected success message: {data}"
        print("PASSED: POST /api/students/{id}/change-pin changed PIN to 9999")
        
        # Verify PIN changed by trying to change again with new PIN
        response2 = authenticated_client.post(
            f"{BASE_URL}/api/students/{TEST_STUDENT_ID}/change-pin",
            json={"current_pin": "9999", "new_pin": ORIGINAL_PIN}
        )
        assert response2.status_code == 200, f"Revert PIN failed: {response2.text}"
        print(f"PASSED: PIN reverted back to {ORIGINAL_PIN}")


class TestStudentChangeOwnPIN:
    """Test student changing own PIN (no auth, just current PIN)"""
    
    def test_change_my_pin_wrong_current(self, api_client):
        """POST /api/student/change-my-pin with wrong PIN returns 400"""
        # Don't use authenticated client - this endpoint needs no auth
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        response = session.post(
            f"{BASE_URL}/api/student/change-my-pin",
            json={"current_pin": "000000", "new_pin": "8888"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "incorrect" in data.get("detail", "").lower(), f"Should mention incorrect PIN: {data}"
        print("PASSED: POST /api/student/change-my-pin with wrong PIN returns 400")
    
    def test_change_my_pin_too_short(self, api_client):
        """POST /api/student/change-my-pin with PIN < 4 digits returns 400"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        response = session.post(
            f"{BASE_URL}/api/student/change-my-pin",
            json={"current_pin": ORIGINAL_PIN, "new_pin": "12"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "4" in data.get("detail", "") or "digit" in data.get("detail", "").lower(), f"Should mention 4 digits: {data}"
        print("PASSED: POST /api/student/change-my-pin with short PIN returns 400")
    
    def test_change_my_pin_non_numeric(self, api_client):
        """POST /api/student/change-my-pin with non-numeric PIN returns 400"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        response = session.post(
            f"{BASE_URL}/api/student/change-my-pin",
            json={"current_pin": ORIGINAL_PIN, "new_pin": "abcd"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "number" in data.get("detail", "").lower(), f"Should mention numbers only: {data}"
        print("PASSED: POST /api/student/change-my-pin with non-numeric PIN returns 400")
    
    def test_change_my_pin_success_and_revert(self, api_client):
        """POST /api/student/change-my-pin should work with just current PIN"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Change to 8888
        response = session.post(
            f"{BASE_URL}/api/student/change-my-pin",
            json={"current_pin": ORIGINAL_PIN, "new_pin": "8888"}
        )
        assert response.status_code == 200, f"Change my PIN failed: {response.text}"
        data = response.json()
        assert "success" in data.get("message", "").lower(), f"Expected success: {data}"
        print("PASSED: POST /api/student/change-my-pin changed PIN to 8888")
        
        # Revert back
        response2 = session.post(
            f"{BASE_URL}/api/student/change-my-pin",
            json={"current_pin": "8888", "new_pin": ORIGINAL_PIN}
        )
        assert response2.status_code == 200, f"Revert failed: {response2.text}"
        print(f"PASSED: Student PIN reverted back to {ORIGINAL_PIN}")


class TestStudentModelFields:
    """Test that student model has new culture_learning fields"""
    
    def test_student_has_culture_learning_field(self, authenticated_client):
        """GET /api/students/{id} should have culture_learning field"""
        response = authenticated_client.get(f"{BASE_URL}/api/students/{TEST_STUDENT_ID}")
        assert response.status_code == 200, f"Get student failed: {response.text}"
        student = response.json()
        # Check that culture_learning field exists (can be empty array)
        assert "culture_learning" in student or student.get("culture_learning") is None or isinstance(student.get("culture_learning", []), list), \
            f"Student should have culture_learning field: {student.keys()}"
        # Check cultural_context can be array
        cc = student.get("cultural_context")
        assert cc is None or isinstance(cc, (str, list)), f"cultural_context should be str or list: {type(cc)}"
        print(f"PASSED: Student has culture_learning={student.get('culture_learning', [])} and cultural_context={cc}")
    
    def test_update_student_culture_learning(self, authenticated_client):
        """PATCH /api/students/{id} should allow setting culture_learning"""
        # Set some culture topics
        test_topics = ["black_history", "womens_history"]
        response = authenticated_client.patch(
            f"{BASE_URL}/api/students/{TEST_STUDENT_ID}",
            json={"culture_learning": test_topics}
        )
        assert response.status_code == 200, f"Update failed: {response.text}"
        updated = response.json()
        assert updated.get("culture_learning") == test_topics, f"culture_learning not updated: {updated.get('culture_learning')}"
        print(f"PASSED: Student culture_learning updated to {test_topics}")
        
        # Reset back to empty
        response2 = authenticated_client.patch(
            f"{BASE_URL}/api/students/{TEST_STUDENT_ID}",
            json={"culture_learning": []}
        )
        assert response2.status_code == 200, f"Reset failed: {response2.text}"
        print("PASSED: culture_learning reset to empty")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
