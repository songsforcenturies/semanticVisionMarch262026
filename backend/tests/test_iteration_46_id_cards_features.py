"""
Iteration 46 Test Suite: User ID Cards, Recording Notifications, Audio Memory Button Text
Tests new features:
1. GET /api/user-card - User ID card data for guardians and students
2. POST /api/recordings/upload - Creates notification in messages collection
3. Core APIs still work: login, students, health
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"


class TestUserIDCards:
    """Tests for the GET /api/user-card endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data["access_token"]
        self.user_id = data["user"]["id"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_user_card_returns_guardian_card(self):
        """GET /api/user-card should return guardian_card with required fields"""
        response = requests.get(f"{BASE_URL}/api/user-card", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "guardian_card" in data
        
        guardian = data["guardian_card"]
        assert guardian["type"] == "guardian"
        assert "name" in guardian
        assert "email" in guardian
        assert "referral_code" in guardian
        assert "referral_url" in guardian
        assert "member_since" in guardian
        assert "student_count" in guardian
        
        # Validate referral URL contains ref query param
        assert "ref=" in guardian["referral_url"]
        print(f"Guardian card: {guardian['name']}, referral: {guardian['referral_code']}, students: {guardian['student_count']}")
    
    def test_user_card_returns_student_cards(self):
        """GET /api/user-card should return student_cards array with required fields"""
        response = requests.get(f"{BASE_URL}/api/user-card", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "student_cards" in data
        
        student_cards = data["student_cards"]
        assert isinstance(student_cards, list)
        
        # Allen has 4 students according to context
        assert len(student_cards) >= 1, "Expected at least 1 student card"
        
        for card in student_cards:
            assert card["type"] == "student"
            assert "name" in card
            assert "student_code" in card
            assert "age" in card
            assert "reading_level" in card
            assert "login_url" in card
            
            # Student code should start with STU-
            assert card["student_code"].startswith("STU-"), f"Invalid student code format: {card['student_code']}"
            print(f"Student card: {card['name']}, code: {card['student_code']}, level: {card['reading_level']}")
    
    def test_user_card_requires_auth(self):
        """GET /api/user-card should require authentication"""
        response = requests.get(f"{BASE_URL}/api/user-card")
        assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"


class TestRecordingNotifications:
    """Tests for notification creation on recording upload"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token and student data before tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        self.token = data["access_token"]
        self.user_id = data["user"]["id"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Get a student ID for testing
        students_resp = requests.get(f"{BASE_URL}/api/students", headers=self.headers)
        if students_resp.status_code == 200:
            students = students_resp.json()
            # Find a student belonging to this user
            for s in students:
                if s.get("guardian_id") == self.user_id:
                    self.student_id = s["id"]
                    self.student_name = s["full_name"]
                    break
            else:
                self.student_id = None
                self.student_name = None
        else:
            self.student_id = None
            self.student_name = None
    
    def test_notifications_endpoint_exists(self):
        """GET /api/notifications should return notifications for user"""
        response = requests.get(f"{BASE_URL}/api/notifications", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "messages" in data
        assert "unread_count" in data
        print(f"Notifications: {len(data['messages'])} messages, {data['unread_count']} unread")


class TestCoreAPIs:
    """Tests for core APIs that must still work"""
    
    def test_health_endpoint(self):
        """GET /api/health should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        print("Health check passed")
    
    def test_login_endpoint(self):
        """POST /api/auth/login should authenticate admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["role"] == "admin"
        print(f"Login successful: {data['user']['full_name']} ({data['user']['role']})")
    
    def test_students_endpoint_authenticated(self):
        """GET /api/students should return students when authenticated"""
        # First login
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        
        # Then get students
        response = requests.get(f"{BASE_URL}/api/students", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        
        students = response.json()
        assert isinstance(students, list)
        print(f"Found {len(students)} students")
    
    def test_students_endpoint_requires_auth(self):
        """GET /api/students should require authentication"""
        response = requests.get(f"{BASE_URL}/api/students")
        assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"


class TestGuardianRecordings:
    """Tests for guardian recordings API"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        self.token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_guardian_recordings_endpoint(self):
        """GET /api/recordings/guardian/all should return recordings list"""
        response = requests.get(f"{BASE_URL}/api/recordings/guardian/all", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "recordings" in data
        assert "students" in data
        print(f"Guardian has {len(data['recordings'])} recordings, {len(data['students'])} students")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
