"""
P0 Bug Fix Tests: Vocabulary Mastered and Agentic Reach Score showing as ZERO
Root Cause: Data type mismatch - mastered_tokens was typed as List[MasteredToken] but 
narrative completion stored tokens as plain strings, causing Pydantic ResponseValidationError (500)
Fix: Changed model to 'list' type, normalized tokens to plain strings
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"
ADMIN_GUARDIAN_ID = "218a24c6-ef31-43ab-ae20-70386f9eede7"
SJ_STUDENT_ID = "18316e14-9f7f-4960-9aba-e809fad104a2"
SJ_EXPECTED_MASTERED = 9
SJ_EXPECTED_SCORE = 93.3


@pytest.fixture(scope="module")
def auth_token():
    """Get admin auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "access_token" in data, "Response missing access_token field"
    return data["access_token"]


@pytest.fixture(scope="module")
def api_client(auth_token):
    """Create authenticated session"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    })
    return session


class TestP0BugFix:
    """P0 Bug Fix: Vocabulary Mastered and Agentic Reach Score showing as ZERO"""

    def test_login_returns_access_token(self):
        """Login endpoint returns access_token field (not 'token')"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        # P0 fix: Response uses 'access_token' field
        assert "access_token" in data, "Response missing 'access_token' field"
        assert "user" in data, "Response missing 'user' field"
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["role"] in ["admin", "guardian"]

    def test_students_endpoint_returns_200(self, api_client):
        """GET /api/students returns 200 (was 500 before fix due to Pydantic validation)"""
        response = api_client.get(f"{BASE_URL}/api/students", params={
            "guardian_id": ADMIN_GUARDIAN_ID
        })
        # P0 fix: This was returning 500 ResponseValidationError before fix
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list of students"
        assert len(data) >= 1, "Expected at least 1 student"

    def test_students_endpoint_has_mastered_tokens(self, api_client):
        """GET /api/students returns mastered_tokens field for each student"""
        response = api_client.get(f"{BASE_URL}/api/students", params={
            "guardian_id": ADMIN_GUARDIAN_ID
        })
        assert response.status_code == 200
        data = response.json()
        for student in data:
            assert "mastered_tokens" in student, f"Student {student['full_name']} missing mastered_tokens"
            assert isinstance(student["mastered_tokens"], list), "mastered_tokens should be a list"

    def test_students_endpoint_has_agentic_reach_score(self, api_client):
        """GET /api/students returns agentic_reach_score field for each student"""
        response = api_client.get(f"{BASE_URL}/api/students", params={
            "guardian_id": ADMIN_GUARDIAN_ID
        })
        assert response.status_code == 200
        data = response.json()
        for student in data:
            assert "agentic_reach_score" in student, f"Student {student['full_name']} missing agentic_reach_score"
            assert isinstance(student["agentic_reach_score"], (int, float)), "agentic_reach_score should be numeric"

    def test_sj_student_has_nonzero_mastered_tokens(self, api_client):
        """SJ student (id: 18316e14) has 9 mastered tokens"""
        response = api_client.get(f"{BASE_URL}/api/students", params={
            "guardian_id": ADMIN_GUARDIAN_ID
        })
        assert response.status_code == 200
        data = response.json()
        sj_student = next((s for s in data if s["id"] == SJ_STUDENT_ID), None)
        assert sj_student is not None, f"SJ student with id {SJ_STUDENT_ID} not found"
        mastered_count = len(sj_student.get("mastered_tokens", []))
        # P0 fix: This was 0 before fix, now should be 9
        assert mastered_count == SJ_EXPECTED_MASTERED, f"Expected {SJ_EXPECTED_MASTERED} mastered tokens, got {mastered_count}"

    def test_sj_student_has_nonzero_score(self, api_client):
        """SJ student (id: 18316e14) has agentic_reach_score of 93.3"""
        response = api_client.get(f"{BASE_URL}/api/students", params={
            "guardian_id": ADMIN_GUARDIAN_ID
        })
        assert response.status_code == 200
        data = response.json()
        sj_student = next((s for s in data if s["id"] == SJ_STUDENT_ID), None)
        assert sj_student is not None
        score = sj_student.get("agentic_reach_score", 0)
        # P0 fix: This was 0 before fix, now should be 93.3
        assert score == pytest.approx(SJ_EXPECTED_SCORE, abs=0.1), f"Expected score ~{SJ_EXPECTED_SCORE}, got {score}"


class TestP0ProgressEndpoint:
    """P0 Bug Fix: /api/students/{student_id}/progress endpoint"""

    def test_progress_endpoint_returns_200(self, api_client):
        """GET /api/students/{student_id}/progress returns 200"""
        response = api_client.get(f"{BASE_URL}/api/students/{SJ_STUDENT_ID}/progress")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_progress_endpoint_has_vocabulary_section(self, api_client):
        """Progress response has vocabulary section with mastered_count"""
        response = api_client.get(f"{BASE_URL}/api/students/{SJ_STUDENT_ID}/progress")
        assert response.status_code == 200
        data = response.json()
        assert "vocabulary" in data, "Response missing 'vocabulary' section"
        assert "mastered_count" in data["vocabulary"], "vocabulary missing 'mastered_count'"
        assert "biological_target" in data["vocabulary"], "vocabulary missing 'biological_target'"

    def test_progress_vocabulary_mastered_count_nonzero(self, api_client):
        """Vocabulary mastered_count is non-zero for SJ student"""
        response = api_client.get(f"{BASE_URL}/api/students/{SJ_STUDENT_ID}/progress")
        assert response.status_code == 200
        data = response.json()
        mastered_count = data["vocabulary"]["mastered_count"]
        # P0 fix: This was 0 before fix
        assert mastered_count == SJ_EXPECTED_MASTERED, f"Expected {SJ_EXPECTED_MASTERED}, got {mastered_count}"

    def test_progress_student_score_nonzero(self, api_client):
        """Student agentic_reach_score is non-zero in progress response"""
        response = api_client.get(f"{BASE_URL}/api/students/{SJ_STUDENT_ID}/progress")
        assert response.status_code == 200
        data = response.json()
        assert "student" in data, "Response missing 'student' section"
        score = data["student"]["agentic_reach_score"]
        # P0 fix: This was 0 before fix
        assert score == pytest.approx(SJ_EXPECTED_SCORE, abs=0.1), f"Expected ~{SJ_EXPECTED_SCORE}, got {score}"

    def test_progress_has_recent_mastered_words(self, api_client):
        """Progress vocabulary has recent_mastered list with actual words"""
        response = api_client.get(f"{BASE_URL}/api/students/{SJ_STUDENT_ID}/progress")
        assert response.status_code == 200
        data = response.json()
        recent = data["vocabulary"]["recent_mastered"]
        assert isinstance(recent, list), "recent_mastered should be a list"
        assert len(recent) > 0, "recent_mastered should have words"
        # Each word should be a string (not a dict - this was part of the P0 bug)
        for word in recent:
            assert isinstance(word, str), f"Word should be string, got {type(word)}: {word}"


class TestLandingPageAndAuth:
    """Test landing page and authentication flow"""

    def test_landing_page_loads(self):
        """Root URL loads without errors"""
        response = requests.get(f"{BASE_URL}/")
        # Frontend is served, should get 200
        assert response.status_code == 200

    def test_admin_login_success(self):
        """Admin user can login with correct credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "admin"

    def test_admin_has_guardian_access(self, api_client):
        """Admin user can access guardian endpoints (has both admin and guardian roles)"""
        # Admin should be able to get students (guardian endpoint)
        response = api_client.get(f"{BASE_URL}/api/students", params={
            "guardian_id": ADMIN_GUARDIAN_ID
        })
        assert response.status_code == 200


class TestDataIntegrity:
    """Verify data integrity after P0 fix"""

    def test_mastered_tokens_are_strings(self, api_client):
        """mastered_tokens are stored as plain strings (not dicts)"""
        response = api_client.get(f"{BASE_URL}/api/students/{SJ_STUDENT_ID}")
        assert response.status_code == 200
        data = response.json()
        for token in data.get("mastered_tokens", []):
            assert isinstance(token, str), f"Token should be string, got {type(token)}: {token}"

    def test_progress_all_mastered_are_strings(self, api_client):
        """Progress endpoint returns all_mastered as strings"""
        response = api_client.get(f"{BASE_URL}/api/students/{SJ_STUDENT_ID}/progress")
        assert response.status_code == 200
        data = response.json()
        for word in data["vocabulary"].get("all_mastered", []):
            assert isinstance(word, str), f"Mastered word should be string, got {type(word)}"
