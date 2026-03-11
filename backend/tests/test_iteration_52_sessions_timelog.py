"""
Iteration 52: Cumulative Time Log Feature Tests

Tests for session tracking endpoints and time-log aggregation API:
- POST /api/sessions/start - creates a new session for a student
- POST /api/sessions/heartbeat - updates last_active and duration of an active session  
- POST /api/sessions/end - ends an active session and calculates final duration
- GET /api/students/{student_id}/time-log - returns aggregated time log data (requires guardian auth)
- GET /api/students/{student_id}/progress - now includes time_log field in response
"""
import pytest
import requests
import time
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
GUARDIAN_EMAIL = "allen@songsforcenturies.com"
GUARDIAN_PASSWORD = "LexiAdmin2026!"
TEST_STUDENT_ID = "18316e14-9f7f-4960-9aba-e809fad104a2"


@pytest.fixture(scope="module")
def auth_token():
    """Get guardian authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": GUARDIAN_EMAIL,
        "password": GUARDIAN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Return headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


class TestSessionStart:
    """Test POST /api/sessions/start endpoint"""

    def test_start_session_success(self):
        """Session start returns session_id and started_at"""
        response = requests.post(f"{BASE_URL}/api/sessions/start", json={
            "student_id": TEST_STUDENT_ID
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "session_id" in data, "Response should contain session_id"
        assert "started_at" in data, "Response should contain started_at"
        assert isinstance(data["session_id"], str), "session_id should be string"
        assert len(data["session_id"]) > 0, "session_id should not be empty"
        print(f"Session started: {data['session_id']}")

    def test_start_session_creates_new_session(self):
        """Starting a session should create a new unique session each time"""
        # Start first session
        resp1 = requests.post(f"{BASE_URL}/api/sessions/start", json={
            "student_id": TEST_STUDENT_ID
        })
        assert resp1.status_code == 200
        session1 = resp1.json()["session_id"]

        # Start second session
        resp2 = requests.post(f"{BASE_URL}/api/sessions/start", json={
            "student_id": TEST_STUDENT_ID
        })
        assert resp2.status_code == 200
        session2 = resp2.json()["session_id"]

        # Session IDs should be different
        assert session1 != session2, "Each session start should create unique session_id"
        print(f"Created unique sessions: {session1[:8]}... and {session2[:8]}...")


class TestSessionHeartbeat:
    """Test POST /api/sessions/heartbeat endpoint"""

    def test_heartbeat_success(self):
        """Heartbeat updates session duration"""
        # Start a session first
        start_resp = requests.post(f"{BASE_URL}/api/sessions/start", json={
            "student_id": TEST_STUDENT_ID
        })
        assert start_resp.status_code == 200
        session_id = start_resp.json()["session_id"]

        # Wait a bit then send heartbeat
        time.sleep(1)
        
        heartbeat_resp = requests.post(f"{BASE_URL}/api/sessions/heartbeat", json={
            "student_id": TEST_STUDENT_ID,
            "session_id": session_id
        })
        assert heartbeat_resp.status_code == 200, f"Expected 200, got {heartbeat_resp.status_code}: {heartbeat_resp.text}"
        
        data = heartbeat_resp.json()
        assert "status" in data, "Response should contain status"
        assert data["status"] == "ok", "Status should be ok"
        assert "duration_seconds" in data, "Response should contain duration_seconds"
        assert data["duration_seconds"] >= 0, "Duration should be non-negative"
        print(f"Heartbeat successful, duration: {data['duration_seconds']}s")

    def test_heartbeat_invalid_session(self):
        """Heartbeat with invalid session_id returns 404"""
        response = requests.post(f"{BASE_URL}/api/sessions/heartbeat", json={
            "student_id": TEST_STUDENT_ID,
            "session_id": "invalid-session-id-12345"
        })
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Heartbeat correctly rejected invalid session")


class TestSessionEnd:
    """Test POST /api/sessions/end endpoint"""

    def test_end_session_success(self):
        """Ending a session returns duration and status"""
        # Start a session
        start_resp = requests.post(f"{BASE_URL}/api/sessions/start", json={
            "student_id": TEST_STUDENT_ID
        })
        assert start_resp.status_code == 200
        session_id = start_resp.json()["session_id"]

        # Wait a bit
        time.sleep(1)

        # End the session
        end_resp = requests.post(f"{BASE_URL}/api/sessions/end", json={
            "student_id": TEST_STUDENT_ID,
            "session_id": session_id
        })
        assert end_resp.status_code == 200, f"Expected 200, got {end_resp.status_code}: {end_resp.text}"
        
        data = end_resp.json()
        assert "status" in data, "Response should contain status"
        assert data["status"] == "ended", "Status should be 'ended'"
        assert "duration_seconds" in data, "Response should contain duration_seconds"
        assert data["duration_seconds"] >= 0, "Duration should be non-negative"
        print(f"Session ended, duration: {data['duration_seconds']}s")

    def test_end_session_already_ended(self):
        """Ending an already ended session returns already_ended status"""
        # Start a session
        start_resp = requests.post(f"{BASE_URL}/api/sessions/start", json={
            "student_id": TEST_STUDENT_ID
        })
        session_id = start_resp.json()["session_id"]

        # End it once
        requests.post(f"{BASE_URL}/api/sessions/end", json={
            "student_id": TEST_STUDENT_ID,
            "session_id": session_id
        })

        # Try to end again
        end_again = requests.post(f"{BASE_URL}/api/sessions/end", json={
            "student_id": TEST_STUDENT_ID,
            "session_id": session_id
        })
        assert end_again.status_code == 200
        assert end_again.json()["status"] == "already_ended"
        print("Double-end correctly returns already_ended")

    def test_heartbeat_after_end_fails(self):
        """Heartbeat on ended session returns 400"""
        # Start and end a session
        start_resp = requests.post(f"{BASE_URL}/api/sessions/start", json={
            "student_id": TEST_STUDENT_ID
        })
        session_id = start_resp.json()["session_id"]
        
        requests.post(f"{BASE_URL}/api/sessions/end", json={
            "student_id": TEST_STUDENT_ID,
            "session_id": session_id
        })

        # Try heartbeat on ended session
        heartbeat_resp = requests.post(f"{BASE_URL}/api/sessions/heartbeat", json={
            "student_id": TEST_STUDENT_ID,
            "session_id": session_id
        })
        assert heartbeat_resp.status_code == 400, f"Expected 400, got {heartbeat_resp.status_code}"
        print("Heartbeat on ended session correctly rejected")


class TestTimeLogAPI:
    """Test GET /api/students/{student_id}/time-log endpoint"""

    def test_get_time_log_success(self, auth_headers):
        """Get time log returns aggregated session data"""
        response = requests.get(
            f"{BASE_URL}/api/students/{TEST_STUDENT_ID}/time-log",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify structure
        assert "student_id" in data, "Response should contain student_id"
        assert "daily_logs" in data, "Response should contain daily_logs"
        assert "total_days_logged_in" in data, "Response should contain total_days_logged_in"
        assert "cumulative_seconds" in data, "Response should contain cumulative_seconds"
        assert "cumulative_display" in data, "Response should contain cumulative_display"
        assert "average_daily_seconds" in data, "Response should contain average_daily_seconds"
        assert "average_daily_display" in data, "Response should contain average_daily_display"
        assert "total_sessions" in data, "Response should contain total_sessions"
        
        # Verify data types
        assert isinstance(data["daily_logs"], list), "daily_logs should be a list"
        assert isinstance(data["total_days_logged_in"], int), "total_days_logged_in should be int"
        assert isinstance(data["cumulative_seconds"], int), "cumulative_seconds should be int"
        
        # Check daily_logs structure if not empty
        if len(data["daily_logs"]) > 0:
            log = data["daily_logs"][0]
            assert "date" in log, "daily_log should contain date"
            assert "total_seconds" in log, "daily_log should contain total_seconds"
            assert "hours" in log, "daily_log should contain hours"
            assert "display" in log, "daily_log should contain display"
        
        print(f"Time log retrieved: {data['total_sessions']} sessions, {data['cumulative_display']} total")

    def test_get_time_log_requires_auth(self):
        """Time log endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/students/{TEST_STUDENT_ID}/time-log")
        # 401 (unauthenticated) or 403 (forbidden) both indicate auth is required
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("Time log correctly requires authentication")

    def test_get_time_log_invalid_student(self, auth_headers):
        """Time log for non-existent student returns 404"""
        response = requests.get(
            f"{BASE_URL}/api/students/invalid-student-id-12345/time-log",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Time log correctly returns 404 for invalid student")


class TestProgressWithTimeLog:
    """Test that GET /api/students/{student_id}/progress includes time_log"""

    def test_progress_includes_time_log(self, auth_headers):
        """Progress endpoint now includes time_log field"""
        response = requests.get(
            f"{BASE_URL}/api/students/{TEST_STUDENT_ID}/progress",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "time_log" in data, "Progress response should include time_log field"
        
        time_log = data["time_log"]
        assert "total_days_logged_in" in time_log, "time_log should contain total_days_logged_in"
        assert "cumulative_seconds" in time_log, "time_log should contain cumulative_seconds"
        assert "total_sessions" in time_log, "time_log should contain total_sessions"
        
        print(f"Progress includes time_log: {time_log['total_sessions']} sessions, {time_log['total_days_logged_in']} days")


class TestSessionFullFlow:
    """Test complete session tracking flow"""

    def test_full_session_lifecycle(self):
        """Test start -> heartbeat -> heartbeat -> end flow"""
        # 1. Start session
        start_resp = requests.post(f"{BASE_URL}/api/sessions/start", json={
            "student_id": TEST_STUDENT_ID
        })
        assert start_resp.status_code == 200
        session_id = start_resp.json()["session_id"]
        print(f"1. Session started: {session_id[:8]}...")

        # 2. First heartbeat
        time.sleep(1)
        hb1 = requests.post(f"{BASE_URL}/api/sessions/heartbeat", json={
            "student_id": TEST_STUDENT_ID,
            "session_id": session_id
        })
        assert hb1.status_code == 200
        duration1 = hb1.json()["duration_seconds"]
        print(f"2. First heartbeat, duration: {duration1}s")

        # 3. Second heartbeat
        time.sleep(1)
        hb2 = requests.post(f"{BASE_URL}/api/sessions/heartbeat", json={
            "student_id": TEST_STUDENT_ID,
            "session_id": session_id
        })
        assert hb2.status_code == 200
        duration2 = hb2.json()["duration_seconds"]
        assert duration2 >= duration1, "Duration should increase over time"
        print(f"3. Second heartbeat, duration: {duration2}s")

        # 4. End session
        end_resp = requests.post(f"{BASE_URL}/api/sessions/end", json={
            "student_id": TEST_STUDENT_ID,
            "session_id": session_id
        })
        assert end_resp.status_code == 200
        final_duration = end_resp.json()["duration_seconds"]
        assert final_duration >= duration2, "Final duration should be >= last heartbeat"
        print(f"4. Session ended, final duration: {final_duration}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
