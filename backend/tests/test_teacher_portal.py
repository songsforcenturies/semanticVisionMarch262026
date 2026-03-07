"""
Teacher Portal Feature Backend API Tests
- Teacher registration with role=teacher (POST /api/auth/register)
- Teacher login and role validation
- Classroom session CRUD (create, list, get, start, end)
- Student join session via code (POST /api/classroom-sessions/join)
- Session analytics (GET /api/classroom-sessions/{id}/analytics)
- Auth prevents guardian from accessing teacher endpoints (403)
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from problem statement
TEST_TEACHER_EMAIL = "smith@school.edu"
TEST_TEACHER_PASSWORD = "Teacher123!"
TEST_GUARDIAN_EMAIL = "testreset@test.com"
TEST_GUARDIAN_PASSWORD = "Test1234!"
TEST_STUDENT_ID = "d32c8a5e-9734-4e8f-8b38-f33a3210d5e8"
EXISTING_SESSION_ID = "bbaa98d0-5b8a-4ba2-bb04-ff2e95892757"
EXISTING_SESSION_CODE = "721279"


class TestTeacherRegistration:
    """Teacher registration (POST /api/auth/register with role=teacher)"""
    
    def test_teacher_registration_new_account(self):
        """Test teacher registration with role=teacher"""
        unique_id = str(uuid.uuid4())[:8]
        teacher_data = {
            "full_name": f"TEST_Teacher_{unique_id}",
            "email": f"test_teacher_{unique_id}@school.edu",
            "password": "TeacherPass123!",
            "role": "teacher"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=teacher_data
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["email"] == teacher_data["email"]
        assert data["full_name"] == teacher_data["full_name"]
        assert data["role"] == "teacher"
        print(f"✓ Teacher registration working ({teacher_data['email']})")
    
    def test_duplicate_teacher_registration_fails(self):
        """Test duplicate teacher email registration fails"""
        unique_id = str(uuid.uuid4())[:8]
        teacher_data = {
            "full_name": f"TEST_Teacher_{unique_id}",
            "email": f"test_teacher_dup_{unique_id}@school.edu",
            "password": "TeacherPass123!",
            "role": "teacher"
        }
        
        # First registration
        first_response = requests.post(f"{BASE_URL}/api/auth/register", json=teacher_data)
        assert first_response.status_code == 200
        
        # Second registration with same email should fail
        second_response = requests.post(f"{BASE_URL}/api/auth/register", json=teacher_data)
        assert second_response.status_code == 400
        assert "already registered" in second_response.json()["detail"].lower()
        print("✓ Duplicate teacher registration correctly rejected")


class TestTeacherLogin:
    """Teacher login and role validation"""
    
    @pytest.fixture(scope="class")
    def teacher_credentials(self):
        """Create and return test teacher credentials"""
        unique_id = str(uuid.uuid4())[:8]
        teacher_data = {
            "full_name": f"TEST_Teacher_{unique_id}",
            "email": f"test_teacher_login_{unique_id}@school.edu",
            "password": "TeacherPass123!",
            "role": "teacher"
        }
        
        # Register
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json=teacher_data)
        assert register_response.status_code == 200
        
        return teacher_data
    
    def test_teacher_login_success(self, teacher_credentials):
        """Test teacher login returns token and user with role=teacher"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": teacher_credentials["email"],
                "password": teacher_credentials["password"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify token returned
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == teacher_credentials["email"]
        assert data["user"]["role"] == "teacher"
        print(f"✓ Teacher login working ({teacher_credentials['email']})")
    
    def test_teacher_login_invalid_credentials(self):
        """Test teacher login with invalid credentials fails"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "nonexistent_teacher@school.edu", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        print("✓ Teacher login with invalid credentials correctly rejected")
    
    def test_login_returns_role_field(self):
        """Verify login response includes role field"""
        # Use existing test teacher or create new
        unique_id = str(uuid.uuid4())[:8]
        teacher_data = {
            "full_name": f"TEST_Teacher_{unique_id}",
            "email": f"test_role_{unique_id}@school.edu",
            "password": "TeacherPass123!",
            "role": "teacher"
        }
        requests.post(f"{BASE_URL}/api/auth/register", json=teacher_data)
        
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": teacher_data["email"], "password": teacher_data["password"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "role" in data["user"]
        print("✓ Login response includes role field")


class TestClassroomSessionCRUD:
    """Classroom session CRUD operations"""
    
    @pytest.fixture(scope="class")
    def authenticated_teacher(self):
        """Create and authenticate a test teacher"""
        unique_id = str(uuid.uuid4())[:8]
        teacher_data = {
            "full_name": f"TEST_Teacher_{unique_id}",
            "email": f"test_teacher_crud_{unique_id}@school.edu",
            "password": "TeacherPass123!",
            "role": "teacher"
        }
        
        # Register
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json=teacher_data)
        assert register_response.status_code == 200
        user_data = register_response.json()
        
        # Login
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": teacher_data["email"], "password": teacher_data["password"]}
        )
        assert login_response.status_code == 200
        auth_data = login_response.json()
        
        return {
            "token": auth_data["access_token"],
            "user": user_data,
            "headers": {"Authorization": f"Bearer {auth_data['access_token']}"}
        }
    
    def test_create_classroom_session(self, authenticated_teacher):
        """Test creating a classroom session (POST /api/classroom-sessions)"""
        session_data = {
            "title": "TEST_Week 4 Vocabulary",
            "description": "Test classroom session",
            "bank_ids": []
        }
        
        response = requests.post(
            f"{BASE_URL}/api/classroom-sessions",
            json=session_data,
            headers=authenticated_teacher["headers"]
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "session_code" in data
        assert len(data["session_code"]) == 6, f"Expected 6-digit session code, got {len(data['session_code'])}"
        assert data["title"] == session_data["title"]
        assert data["status"] == "waiting"
        assert data["teacher_id"] == authenticated_teacher["user"]["id"]
        assert "participating_students" in data
        assert "created_date" in data
        print(f"✓ Classroom session created (code: {data['session_code']})")
        return data
    
    def test_list_classroom_sessions(self, authenticated_teacher):
        """Test listing classroom sessions (GET /api/classroom-sessions)"""
        # Create a session first
        session_data = {"title": "TEST_List Session", "description": "", "bank_ids": []}
        requests.post(
            f"{BASE_URL}/api/classroom-sessions",
            json=session_data,
            headers=authenticated_teacher["headers"]
        )
        
        response = requests.get(
            f"{BASE_URL}/api/classroom-sessions",
            headers=authenticated_teacher["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check structure of first session
        first_session = data[0]
        assert "id" in first_session
        assert "title" in first_session
        assert "session_code" in first_session
        assert "status" in first_session
        print(f"✓ Classroom sessions list working ({len(data)} sessions)")
    
    def test_get_classroom_session_by_id(self, authenticated_teacher):
        """Test getting a specific classroom session (GET /api/classroom-sessions/{id})"""
        # Create a session first
        create_response = requests.post(
            f"{BASE_URL}/api/classroom-sessions",
            json={"title": "TEST_Get Session", "description": "", "bank_ids": []},
            headers=authenticated_teacher["headers"]
        )
        assert create_response.status_code == 200
        created_session = create_response.json()
        
        # Get by ID
        response = requests.get(
            f"{BASE_URL}/api/classroom-sessions/{created_session['id']}",
            headers=authenticated_teacher["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == created_session["id"]
        assert data["session_code"] == created_session["session_code"]
        print(f"✓ Get classroom session by ID working")
    
    def test_start_classroom_session(self, authenticated_teacher):
        """Test starting a classroom session (POST /api/classroom-sessions/{id}/start)"""
        # Create a session first
        create_response = requests.post(
            f"{BASE_URL}/api/classroom-sessions",
            json={"title": "TEST_Start Session", "description": "", "bank_ids": []},
            headers=authenticated_teacher["headers"]
        )
        assert create_response.status_code == 200
        created_session = create_response.json()
        assert created_session["status"] == "waiting"
        
        # Start the session
        response = requests.post(
            f"{BASE_URL}/api/classroom-sessions/{created_session['id']}/start",
            headers=authenticated_teacher["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        print(f"✓ Start classroom session working")
    
    def test_end_classroom_session(self, authenticated_teacher):
        """Test ending a classroom session (POST /api/classroom-sessions/{id}/end)"""
        # Create and start a session first
        create_response = requests.post(
            f"{BASE_URL}/api/classroom-sessions",
            json={"title": "TEST_End Session", "description": "", "bank_ids": []},
            headers=authenticated_teacher["headers"]
        )
        assert create_response.status_code == 200
        created_session = create_response.json()
        
        # Start the session
        requests.post(
            f"{BASE_URL}/api/classroom-sessions/{created_session['id']}/start",
            headers=authenticated_teacher["headers"]
        )
        
        # End the session
        response = requests.post(
            f"{BASE_URL}/api/classroom-sessions/{created_session['id']}/end",
            headers=authenticated_teacher["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        print(f"✓ End classroom session working")
    
    def test_create_session_requires_auth(self):
        """Test that creating session requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/classroom-sessions",
            json={"title": "Unauthorized Session", "description": "", "bank_ids": []}
        )
        assert response.status_code in [401, 403]
        print("✓ Create session requires authentication")
    
    def test_list_sessions_requires_auth(self):
        """Test that listing sessions requires authentication"""
        response = requests.get(f"{BASE_URL}/api/classroom-sessions")
        assert response.status_code in [401, 403]
        print("✓ List sessions requires authentication")


class TestStudentJoinSession:
    """Student join session via code (POST /api/classroom-sessions/join)"""
    
    @pytest.fixture(scope="class")
    def teacher_with_session(self):
        """Create teacher with an active session"""
        unique_id = str(uuid.uuid4())[:8]
        teacher_data = {
            "full_name": f"TEST_Teacher_{unique_id}",
            "email": f"test_teacher_join_{unique_id}@school.edu",
            "password": "TeacherPass123!",
            "role": "teacher"
        }
        
        # Register
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json=teacher_data)
        assert register_response.status_code == 200
        user_data = register_response.json()
        
        # Login
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": teacher_data["email"], "password": teacher_data["password"]}
        )
        auth_data = login_response.json()
        headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
        
        # Create session
        create_response = requests.post(
            f"{BASE_URL}/api/classroom-sessions",
            json={"title": "TEST_Join Session", "description": "", "bank_ids": []},
            headers=headers
        )
        session = create_response.json()
        
        return {
            "headers": headers,
            "session": session,
            "user": user_data
        }
    
    def test_student_join_session_success(self, teacher_with_session):
        """Test student joining session via code"""
        response = requests.post(
            f"{BASE_URL}/api/classroom-sessions/join",
            json={
                "session_code": teacher_with_session["session"]["session_code"],
                "student_id": TEST_STUDENT_ID
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "session_id" in data
        assert "message" in data
        print(f"✓ Student join session working")
    
    def test_student_join_invalid_code(self):
        """Test student join with invalid code fails"""
        response = requests.post(
            f"{BASE_URL}/api/classroom-sessions/join",
            json={
                "session_code": "000000",
                "student_id": TEST_STUDENT_ID
            }
        )
        assert response.status_code == 404
        print("✓ Student join with invalid code correctly rejected")
    
    def test_student_join_already_joined(self, teacher_with_session):
        """Test student already joined returns appropriate response"""
        # First join
        requests.post(
            f"{BASE_URL}/api/classroom-sessions/join",
            json={
                "session_code": teacher_with_session["session"]["session_code"],
                "student_id": TEST_STUDENT_ID
            }
        )
        
        # Second join (already joined)
        response = requests.post(
            f"{BASE_URL}/api/classroom-sessions/join",
            json={
                "session_code": teacher_with_session["session"]["session_code"],
                "student_id": TEST_STUDENT_ID
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "Already joined" in data.get("message", "")
        print("✓ Student already joined handled correctly")
    
    def test_join_with_invalid_student(self, teacher_with_session):
        """Test join with non-existent student ID fails"""
        response = requests.post(
            f"{BASE_URL}/api/classroom-sessions/join",
            json={
                "session_code": teacher_with_session["session"]["session_code"],
                "student_id": "nonexistent-student-id"
            }
        )
        assert response.status_code == 404
        print("✓ Join with invalid student ID correctly rejected")


class TestSessionAnalytics:
    """Session analytics endpoint (GET /api/classroom-sessions/{id}/analytics)"""
    
    @pytest.fixture(scope="class")
    def teacher_with_populated_session(self):
        """Create teacher with session that has students"""
        unique_id = str(uuid.uuid4())[:8]
        teacher_data = {
            "full_name": f"TEST_Teacher_{unique_id}",
            "email": f"test_teacher_analytics_{unique_id}@school.edu",
            "password": "TeacherPass123!",
            "role": "teacher"
        }
        
        # Register
        requests.post(f"{BASE_URL}/api/auth/register", json=teacher_data)
        
        # Login
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": teacher_data["email"], "password": teacher_data["password"]}
        )
        auth_data = login_response.json()
        headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
        
        # Create session
        create_response = requests.post(
            f"{BASE_URL}/api/classroom-sessions",
            json={"title": "TEST_Analytics Session", "description": "", "bank_ids": []},
            headers=headers
        )
        session = create_response.json()
        
        # Add a student
        requests.post(
            f"{BASE_URL}/api/classroom-sessions/join",
            json={"session_code": session["session_code"], "student_id": TEST_STUDENT_ID}
        )
        
        return {"headers": headers, "session": session}
    
    def test_get_session_analytics(self, teacher_with_populated_session):
        """Test getting session analytics"""
        response = requests.get(
            f"{BASE_URL}/api/classroom-sessions/{teacher_with_populated_session['session']['id']}/analytics",
            headers=teacher_with_populated_session["headers"]
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "session" in data
        assert "students" in data
        assert "class_summary" in data
        
        # Session info
        assert data["session"]["id"] == teacher_with_populated_session["session"]["id"]
        assert "student_count" in data["session"]
        
        # Class summary
        assert "avg_accuracy" in data["class_summary"]
        assert "total_assessments" in data["class_summary"]
        assert "total_words_mastered" in data["class_summary"]
        assert "avg_reading_seconds" in data["class_summary"]
        
        print(f"✓ Session analytics working ({data['session']['student_count']} students)")
    
    def test_analytics_requires_auth(self):
        """Test analytics requires authentication"""
        response = requests.get(f"{BASE_URL}/api/classroom-sessions/fake-id/analytics")
        assert response.status_code in [401, 403]
        print("✓ Analytics requires authentication")
    
    def test_analytics_empty_session(self):
        """Test analytics for empty session"""
        unique_id = str(uuid.uuid4())[:8]
        teacher_data = {
            "full_name": f"TEST_Teacher_{unique_id}",
            "email": f"test_teacher_empty_{unique_id}@school.edu",
            "password": "TeacherPass123!",
            "role": "teacher"
        }
        
        requests.post(f"{BASE_URL}/api/auth/register", json=teacher_data)
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": teacher_data["email"], "password": teacher_data["password"]}
        )
        auth_data = login_response.json()
        headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
        
        # Create empty session
        create_response = requests.post(
            f"{BASE_URL}/api/classroom-sessions",
            json={"title": "TEST_Empty Session", "description": "", "bank_ids": []},
            headers=headers
        )
        session = create_response.json()
        
        # Get analytics
        response = requests.get(
            f"{BASE_URL}/api/classroom-sessions/{session['id']}/analytics",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["session"]["student_count"] == 0
        assert data["class_summary"]["avg_accuracy"] == 0
        print("✓ Analytics for empty session works correctly")


class TestGuardianAccessRestriction:
    """Auth prevents guardian from accessing teacher endpoints (returns 403)"""
    
    @pytest.fixture(scope="class")
    def authenticated_guardian(self):
        """Get authenticated guardian"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_GUARDIAN_EMAIL, "password": TEST_GUARDIAN_PASSWORD}
        )
        if response.status_code != 200:
            # Create new guardian
            unique_id = str(uuid.uuid4())[:8]
            guardian_data = {
                "full_name": f"TEST_Guardian_{unique_id}",
                "email": f"test_guardian_{unique_id}@example.com",
                "password": "TestPass123!",
                "role": "guardian"
            }
            requests.post(f"{BASE_URL}/api/auth/register", json=guardian_data)
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": guardian_data["email"], "password": guardian_data["password"]}
            )
        
        auth_data = response.json()
        return {"headers": {"Authorization": f"Bearer {auth_data['access_token']}"}}
    
    def test_guardian_cannot_create_session(self, authenticated_guardian):
        """Test guardian cannot create classroom session (403)"""
        response = requests.post(
            f"{BASE_URL}/api/classroom-sessions",
            json={"title": "Guardian Session", "description": "", "bank_ids": []},
            headers=authenticated_guardian["headers"]
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Guardian cannot create classroom session (403)")
    
    def test_guardian_cannot_list_sessions(self, authenticated_guardian):
        """Test guardian cannot list classroom sessions (403)"""
        response = requests.get(
            f"{BASE_URL}/api/classroom-sessions",
            headers=authenticated_guardian["headers"]
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Guardian cannot list classroom sessions (403)")
    
    def test_guardian_cannot_start_session(self, authenticated_guardian):
        """Test guardian cannot start session (403)"""
        response = requests.post(
            f"{BASE_URL}/api/classroom-sessions/{EXISTING_SESSION_ID}/start",
            headers=authenticated_guardian["headers"]
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Guardian cannot start classroom session (403)")
    
    def test_guardian_cannot_end_session(self, authenticated_guardian):
        """Test guardian cannot end session (403)"""
        response = requests.post(
            f"{BASE_URL}/api/classroom-sessions/{EXISTING_SESSION_ID}/end",
            headers=authenticated_guardian["headers"]
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Guardian cannot end classroom session (403)")
    
    def test_guardian_cannot_get_analytics(self, authenticated_guardian):
        """Test guardian cannot get session analytics (403)"""
        response = requests.get(
            f"{BASE_URL}/api/classroom-sessions/{EXISTING_SESSION_ID}/analytics",
            headers=authenticated_guardian["headers"]
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Guardian cannot access session analytics (403)")


class TestExistingSession:
    """Test with existing session from problem statement"""
    
    @pytest.fixture(scope="class")
    def existing_teacher_token(self):
        """Login as existing teacher or create new"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_TEACHER_EMAIL, "password": TEST_TEACHER_PASSWORD}
        )
        if response.status_code == 200:
            auth_data = response.json()
            return {"Authorization": f"Bearer {auth_data['access_token']}"}
        
        # Teacher doesn't exist, create new
        unique_id = str(uuid.uuid4())[:8]
        teacher_data = {
            "full_name": f"TEST_Teacher_{unique_id}",
            "email": f"test_teacher_exist_{unique_id}@school.edu",
            "password": "TeacherPass123!",
            "role": "teacher"
        }
        requests.post(f"{BASE_URL}/api/auth/register", json=teacher_data)
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": teacher_data["email"], "password": teacher_data["password"]}
        )
        auth_data = response.json()
        return {"Authorization": f"Bearer {auth_data['access_token']}"}
    
    def test_join_existing_session_by_code(self):
        """Test joining existing session (721279)"""
        response = requests.post(
            f"{BASE_URL}/api/classroom-sessions/join",
            json={"session_code": EXISTING_SESSION_CODE, "student_id": TEST_STUDENT_ID}
        )
        # May return 200 (joined) or 200 (already joined) or 404 (session ended/not found)
        if response.status_code == 200:
            print(f"✓ Join existing session working (code: {EXISTING_SESSION_CODE})")
        elif response.status_code == 404:
            print(f"⚠ Existing session may be completed or not found (code: {EXISTING_SESSION_CODE})")
        else:
            pytest.fail(f"Unexpected status: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
