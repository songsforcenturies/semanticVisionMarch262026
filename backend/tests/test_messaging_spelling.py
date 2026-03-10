"""
Backend API tests for Admin Messaging and Spelling Contests features.
Tests: POST/GET/DELETE admin messages, GET notifications, 
       POST/GET admin spelling contests, POST submit, GET leaderboard.
"""

import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://patent-filing-deploy.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"
STUDENT_CODE = "STU-DR40V7"
STUDENT_PIN = "914027"


class TestAdminMessaging:
    """Tests for Admin Messaging endpoints"""

    @pytest.fixture(scope="class")
    def admin_token(self):
        """Login as admin and get token"""
        res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD
        })
        assert res.status_code == 200, f"Admin login failed: {res.text}"
        return res.json()["access_token"]

    @pytest.fixture(scope="class")
    def admin_headers(self, admin_token):
        """Return headers with admin auth"""
        return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}

    @pytest.fixture(scope="class")
    def student_data(self):
        """Login as student and get data"""
        res = requests.post(f"{BASE_URL}/api/auth/student-login", json={
            "student_code": STUDENT_CODE, "pin": STUDENT_PIN
        })
        assert res.status_code == 200, f"Student login failed: {res.text}"
        return res.json()["student"]

    def test_admin_create_message(self, admin_headers):
        """POST /api/admin/messages - Create admin message"""
        payload = {
            "title": "TEST_Message_Title",
            "body": "This is a test message body for testing purposes.",
            "target": "all",
            "priority": "normal"
        }
        res = requests.post(f"{BASE_URL}/api/admin/messages", json=payload, headers=admin_headers)
        assert res.status_code == 200, f"Create message failed: {res.text}"
        data = res.json()
        assert data["title"] == "TEST_Message_Title"
        assert data["body"] == "This is a test message body for testing purposes."
        assert data["target"] == "all"
        assert data["priority"] == "normal"
        assert "id" in data
        assert "created_date" in data
        print(f"✓ Admin message created: {data['id']}")
        return data["id"]

    def test_admin_list_messages(self, admin_headers):
        """GET /api/admin/messages - List admin messages"""
        res = requests.get(f"{BASE_URL}/api/admin/messages", headers=admin_headers)
        assert res.status_code == 200, f"List messages failed: {res.text}"
        data = res.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Admin messages listed: {len(data)} messages")

    def test_user_notifications(self, admin_headers):
        """GET /api/notifications - Get user notifications"""
        res = requests.get(f"{BASE_URL}/api/notifications", headers=admin_headers)
        assert res.status_code == 200, f"Get notifications failed: {res.text}"
        data = res.json()
        assert "messages" in data
        assert "unread_count" in data
        assert isinstance(data["messages"], list)
        assert isinstance(data["unread_count"], int)
        print(f"✓ User notifications: {len(data['messages'])} messages, {data['unread_count']} unread")

    def test_student_notifications(self, student_data):
        """GET /api/student-notifications/{student_id} - Get student notifications"""
        student_id = student_data["id"]
        res = requests.get(f"{BASE_URL}/api/student-notifications/{student_id}")
        assert res.status_code == 200, f"Get student notifications failed: {res.text}"
        data = res.json()
        assert "messages" in data
        assert "unread_count" in data
        print(f"✓ Student notifications: {len(data['messages'])} messages, {data['unread_count']} unread")

    def test_mark_notification_read(self, admin_headers):
        """POST /api/notifications/{id}/read - Mark notification as read"""
        # First get messages to find one
        res = requests.get(f"{BASE_URL}/api/admin/messages", headers=admin_headers)
        msgs = res.json()
        if not msgs:
            pytest.skip("No messages to mark as read")
        
        msg_id = msgs[0]["id"]
        res = requests.post(f"{BASE_URL}/api/notifications/{msg_id}/read", headers=admin_headers)
        assert res.status_code == 200, f"Mark read failed: {res.text}"
        data = res.json()
        assert data.get("status") == "read"
        print(f"✓ Notification marked as read: {msg_id}")

    def test_admin_delete_message(self, admin_headers):
        """DELETE /api/admin/messages/{id} - Delete admin message"""
        # First create a message to delete
        payload = {"title": "TEST_Delete_Me", "body": "Test delete", "target": "all", "priority": "low"}
        create_res = requests.post(f"{BASE_URL}/api/admin/messages", json=payload, headers=admin_headers)
        assert create_res.status_code == 200
        msg_id = create_res.json()["id"]
        
        # Delete it
        res = requests.delete(f"{BASE_URL}/api/admin/messages/{msg_id}", headers=admin_headers)
        assert res.status_code == 200, f"Delete message failed: {res.text}"
        data = res.json()
        assert data.get("status") == "deleted"
        print(f"✓ Admin message deleted: {msg_id}")


class TestSpellingContests:
    """Tests for Spelling Contest endpoints"""

    @pytest.fixture(scope="class")
    def admin_token(self):
        """Login as admin and get token"""
        res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD
        })
        assert res.status_code == 200, f"Admin login failed: {res.text}"
        return res.json()["access_token"]

    @pytest.fixture(scope="class")
    def admin_headers(self, admin_token):
        """Return headers with admin auth"""
        return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}

    @pytest.fixture(scope="class")
    def student_data(self):
        """Login as student and get data"""
        res = requests.post(f"{BASE_URL}/api/auth/student-login", json={
            "student_code": STUDENT_CODE, "pin": STUDENT_PIN
        })
        assert res.status_code == 200, f"Student login failed: {res.text}"
        return res.json()["student"]

    def test_admin_create_spelling_contest(self, admin_headers):
        """POST /api/admin/spelling-contests - Create spelling contest"""
        start_date = datetime.utcnow().isoformat()
        end_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        
        payload = {
            "title": "TEST_Spelling_Bee_Contest",
            "description": "Test contest for automated testing",
            "word_list": ["beautiful", "knowledge", "science", "adventure", "rhythm"],
            "time_limit_seconds": 120,
            "start_date": start_date,
            "end_date": end_date
        }
        res = requests.post(f"{BASE_URL}/api/admin/spelling-contests", json=payload, headers=admin_headers)
        assert res.status_code == 200, f"Create contest failed: {res.text}"
        data = res.json()
        assert data["title"] == "TEST_Spelling_Bee_Contest"
        assert data["word_list"] == ["beautiful", "knowledge", "science", "adventure", "rhythm"]
        assert data["time_limit_seconds"] == 120
        assert data["is_active"] == True
        assert "id" in data
        print(f"✓ Spelling contest created: {data['id']}")
        return data["id"]

    def test_admin_list_spelling_contests(self, admin_headers):
        """GET /api/admin/spelling-contests - List all spelling contests"""
        res = requests.get(f"{BASE_URL}/api/admin/spelling-contests", headers=admin_headers)
        assert res.status_code == 200, f"List contests failed: {res.text}"
        data = res.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Spelling contests listed: {len(data)} contests")

    def test_get_active_spelling_contests(self):
        """GET /api/spelling-contests - Get active contests (public endpoint)"""
        res = requests.get(f"{BASE_URL}/api/spelling-contests")
        assert res.status_code == 200, f"Get active contests failed: {res.text}"
        data = res.json()
        assert isinstance(data, list), "Response should be a list"
        for contest in data:
            assert contest.get("is_active") == True
            assert "participant_count" in contest
        print(f"✓ Active spelling contests: {len(data)} found")

    def test_submit_spelling_contest(self, student_data, admin_headers):
        """POST /api/spelling-contests/submit - Submit spelling answers"""
        # First get an active contest
        res = requests.get(f"{BASE_URL}/api/spelling-contests")
        contests = res.json()
        if not contests:
            # Create one for testing
            start_date = datetime.utcnow().isoformat()
            end_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
            payload = {
                "title": "TEST_Submit_Contest",
                "word_list": ["cat", "dog", "bird"],
                "time_limit_seconds": 60,
                "start_date": start_date,
                "end_date": end_date
            }
            res = requests.post(f"{BASE_URL}/api/admin/spelling-contests", json=payload, headers=admin_headers)
            contest = res.json()
        else:
            contest = contests[0]
        
        contest_id = contest["id"]
        word_list = contest["word_list"]
        
        # Submit answers - get some correct, some wrong
        answers = {}
        for i, word in enumerate(word_list):
            if i % 2 == 0:  # Correct answer
                answers[word] = word
            else:  # Wrong answer
                answers[word] = word + "xyz"
        
        submit_payload = {
            "contest_id": contest_id,
            "student_id": student_data["id"],
            "student_name": student_data["full_name"],
            "answers": answers,
            "time_taken_seconds": 45
        }
        
        res = requests.post(f"{BASE_URL}/api/spelling-contests/submit", json=submit_payload)
        assert res.status_code == 200, f"Submit contest failed: {res.text}"
        data = res.json()
        assert "score" in data
        assert "correct_count" in data
        assert "total_words" in data
        assert "results" in data
        assert data["student_id"] == student_data["id"]
        print(f"✓ Spelling submission: {data['correct_count']}/{data['total_words']} correct, {data['score']}%")

    def test_get_spelling_leaderboard(self, admin_headers):
        """GET /api/spelling-contests/{id}/leaderboard - Get leaderboard"""
        # Get a contest
        res = requests.get(f"{BASE_URL}/api/admin/spelling-contests", headers=admin_headers)
        contests = res.json()
        if not contests:
            pytest.skip("No contests available for leaderboard")
        
        contest_id = contests[0]["id"]
        res = requests.get(f"{BASE_URL}/api/spelling-contests/{contest_id}/leaderboard")
        assert res.status_code == 200, f"Get leaderboard failed: {res.text}"
        data = res.json()
        assert isinstance(data, list), "Response should be a list"
        for entry in data:
            assert "rank" in entry
            assert "student_name" in entry
            assert "score" in entry
        print(f"✓ Leaderboard retrieved: {len(data)} entries")

    def test_admin_toggle_spelling_contest(self, admin_headers):
        """PUT /api/admin/spelling-contests/{id}/toggle - Toggle contest active status"""
        res = requests.get(f"{BASE_URL}/api/admin/spelling-contests", headers=admin_headers)
        contests = res.json()
        if not contests:
            pytest.skip("No contests to toggle")
        
        contest_id = contests[0]["id"]
        original_status = contests[0].get("is_active", True)
        
        res = requests.put(f"{BASE_URL}/api/admin/spelling-contests/{contest_id}/toggle", headers=admin_headers)
        assert res.status_code == 200, f"Toggle contest failed: {res.text}"
        data = res.json()
        assert "is_active" in data
        assert data["is_active"] == (not original_status)
        print(f"✓ Contest toggled: {original_status} -> {data['is_active']}")
        
        # Toggle back to original state
        requests.put(f"{BASE_URL}/api/admin/spelling-contests/{contest_id}/toggle", headers=admin_headers)

    def test_admin_delete_spelling_contest(self, admin_headers):
        """DELETE /api/admin/spelling-contests/{id} - Delete spelling contest"""
        # Create a contest to delete
        start_date = datetime.utcnow().isoformat()
        end_date = (datetime.utcnow() + timedelta(days=1)).isoformat()
        
        payload = {
            "title": "TEST_Delete_Contest",
            "word_list": ["test", "delete"],
            "time_limit_seconds": 30,
            "start_date": start_date,
            "end_date": end_date
        }
        create_res = requests.post(f"{BASE_URL}/api/admin/spelling-contests", json=payload, headers=admin_headers)
        assert create_res.status_code == 200
        contest_id = create_res.json()["id"]
        
        # Delete it
        res = requests.delete(f"{BASE_URL}/api/admin/spelling-contests/{contest_id}", headers=admin_headers)
        assert res.status_code == 200, f"Delete contest failed: {res.text}"
        data = res.json()
        assert data.get("status") == "deleted"
        print(f"✓ Spelling contest deleted: {contest_id}")


class TestWordBankMarketplace:
    """Tests for word bank price visibility (related to marketplace fixes)"""

    @pytest.fixture(scope="class")
    def admin_headers(self):
        res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD
        })
        assert res.status_code == 200
        return {"Authorization": f"Bearer {res.json()['access_token']}", "Content-Type": "application/json"}

    def test_word_banks_have_price_field(self, admin_headers):
        """GET /api/word-banks - Verify word banks have price field"""
        res = requests.get(f"{BASE_URL}/api/word-banks", headers=admin_headers)
        assert res.status_code == 200, f"Get word banks failed: {res.text}"
        data = res.json()
        assert isinstance(data, list)
        
        for bank in data[:5]:  # Check first 5
            assert "price" in bank, f"Bank {bank.get('name')} missing price field"
            assert isinstance(bank["price"], (int, float))
        
        print(f"✓ Word banks have price field: {len(data)} banks checked")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
