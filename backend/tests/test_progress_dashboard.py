"""
Student Progress Dashboard API Tests
- GET /api/students/{id}/progress endpoint
- Guardian authentication and authorization
- Empty states and data aggregation
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from review_request
TEST_GUARDIAN_EMAIL = "testreset@test.com"
TEST_GUARDIAN_PASSWORD = "Test1234!"
TEST_STUDENT_ID = "d32c8a5e-9734-4e8f-8b38-f33a3210d5e8"  # PinTest Kid


class TestProgressEndpointAuth:
    """Test authentication and authorization for progress endpoint"""
    
    @pytest.fixture
    def guardian_auth(self):
        """Login as the test guardian and return auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_GUARDIAN_EMAIL, "password": TEST_GUARDIAN_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Cannot login as test guardian: {response.status_code}")
        
        data = response.json()
        return {
            "token": data["access_token"],
            "user": data["user"],
            "headers": {"Authorization": f"Bearer {data['access_token']}"}
        }
    
    @pytest.fixture
    def other_guardian_auth(self):
        """Create and login as a different guardian"""
        unique_id = str(uuid.uuid4())[:8]
        guardian_data = {
            "full_name": f"TEST_OtherGuardian_{unique_id}",
            "email": f"test_other_{unique_id}@example.com",
            "password": "TestPass123!",
            "role": "guardian"
        }
        
        # Register
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=guardian_data
        )
        if register_response.status_code != 200:
            pytest.skip(f"Cannot register other guardian: {register_response.status_code}")
        
        # Login
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": guardian_data["email"], "password": guardian_data["password"]}
        )
        if login_response.status_code != 200:
            pytest.skip(f"Cannot login as other guardian: {login_response.status_code}")
        
        data = login_response.json()
        return {
            "token": data["access_token"],
            "user": data["user"],
            "headers": {"Authorization": f"Bearer {data['access_token']}"}
        }
    
    def test_progress_requires_authentication(self):
        """Test that progress endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/students/{TEST_STUDENT_ID}/progress")
        # FastAPI returns 403 when no auth header (Forbidden) or 401 (Unauthorized)
        assert response.status_code in [401, 403], f"Expected 401/403 for no auth, got {response.status_code}"
        print("✓ Progress endpoint requires authentication")
    
    def test_progress_rejects_unauthorized_guardian(self, guardian_auth, other_guardian_auth):
        """Test that a guardian cannot view another guardian's student progress"""
        # First verify test student belongs to test guardian
        response = requests.get(
            f"{BASE_URL}/api/students/{TEST_STUDENT_ID}/progress",
            headers=guardian_auth["headers"]
        )
        # Should succeed for the owner guardian
        if response.status_code == 200:
            # Now try with other guardian
            other_response = requests.get(
                f"{BASE_URL}/api/students/{TEST_STUDENT_ID}/progress",
                headers=other_guardian_auth["headers"]
            )
            assert other_response.status_code == 403, f"Expected 403 Forbidden, got {other_response.status_code}"
            print("✓ Progress endpoint rejects unauthorized guardian access")
        else:
            pytest.skip(f"Test student not found or inaccessible: {response.status_code}")


class TestProgressEndpointData:
    """Test progress endpoint returns correct data structure"""
    
    @pytest.fixture
    def guardian_auth(self):
        """Login as the test guardian and return auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_GUARDIAN_EMAIL, "password": TEST_GUARDIAN_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Cannot login as test guardian: {response.status_code}")
        
        data = response.json()
        return {
            "token": data["access_token"],
            "user": data["user"],
            "headers": {"Authorization": f"Bearer {data['access_token']}"}
        }
    
    def test_progress_returns_correct_structure(self, guardian_auth):
        """Test progress endpoint returns correct data structure"""
        response = requests.get(
            f"{BASE_URL}/api/students/{TEST_STUDENT_ID}/progress",
            headers=guardian_auth["headers"]
        )
        
        # If student not found, first create a test student
        if response.status_code == 404:
            print(f"Student {TEST_STUDENT_ID} not found - creating test student...")
            # Create a test student
            unique_id = str(uuid.uuid4())[:8]
            student_data = {
                "guardian_id": guardian_auth["user"]["id"],
                "full_name": f"TEST_ProgressStudent_{unique_id}",
                "age": 10,
                "grade_level": "1-12",
                "interests": ["reading"],
                "virtues": ["curiosity", "kindness"]
            }
            create_response = requests.post(
                f"{BASE_URL}/api/students",
                json=student_data,
                headers=guardian_auth["headers"]
            )
            assert create_response.status_code == 200, f"Failed to create test student: {create_response.text}"
            created_student = create_response.json()
            student_id = created_student["id"]
            
            # Get progress for the new student
            response = requests.get(
                f"{BASE_URL}/api/students/{student_id}/progress",
                headers=guardian_auth["headers"]
            )
        
        assert response.status_code == 200, f"Failed to get progress: {response.status_code} - {response.text}"
        
        data = response.json()
        
        # Verify top-level structure
        assert "student" in data, "Missing 'student' in response"
        assert "reading_stats" in data, "Missing 'reading_stats' in response"
        assert "vocabulary" in data, "Missing 'vocabulary' in response"
        assert "assessments" in data, "Missing 'assessments' in response"
        assert "narratives" in data, "Missing 'narratives' in response"
        assert "assigned_banks" in data, "Missing 'assigned_banks' in response"
        
        print("✓ Progress endpoint returns correct top-level structure")
        return data
    
    def test_progress_student_data(self, guardian_auth):
        """Test student data in progress response"""
        # First get/create a student
        students_response = requests.get(
            f"{BASE_URL}/api/students",
            params={"guardian_id": guardian_auth["user"]["id"]},
            headers=guardian_auth["headers"]
        )
        assert students_response.status_code == 200
        students = students_response.json()
        
        if not students:
            pytest.skip("No students found for this guardian")
        
        student_id = students[0]["id"]
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/progress",
            headers=guardian_auth["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify student data structure
        student = data["student"]
        assert "id" in student
        assert "full_name" in student
        assert "biological_target" in student
        assert "virtues" in student
        assert "agentic_reach_score" in student
        
        print(f"✓ Student data structure correct for: {student['full_name']}")
    
    def test_progress_reading_stats_structure(self, guardian_auth):
        """Test reading stats structure in progress response"""
        students_response = requests.get(
            f"{BASE_URL}/api/students",
            params={"guardian_id": guardian_auth["user"]["id"]},
            headers=guardian_auth["headers"]
        )
        assert students_response.status_code == 200
        students = students_response.json()
        
        if not students:
            pytest.skip("No students found for this guardian")
        
        student_id = students[0]["id"]
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/progress",
            headers=guardian_auth["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify reading stats structure
        reading_stats = data["reading_stats"]
        assert "total_reading_seconds" in reading_stats
        assert "total_words_read" in reading_stats
        assert "average_wpm" in reading_stats
        assert "sessions_count" in reading_stats
        
        # Values should be numbers
        assert isinstance(reading_stats["total_reading_seconds"], (int, float))
        assert isinstance(reading_stats["total_words_read"], (int, float))
        assert isinstance(reading_stats["average_wpm"], (int, float))
        assert isinstance(reading_stats["sessions_count"], (int, float))
        
        print(f"✓ Reading stats structure correct")
    
    def test_progress_vocabulary_structure(self, guardian_auth):
        """Test vocabulary data structure in progress response"""
        students_response = requests.get(
            f"{BASE_URL}/api/students",
            params={"guardian_id": guardian_auth["user"]["id"]},
            headers=guardian_auth["headers"]
        )
        assert students_response.status_code == 200
        students = students_response.json()
        
        if not students:
            pytest.skip("No students found for this guardian")
        
        student_id = students[0]["id"]
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/progress",
            headers=guardian_auth["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify vocabulary structure
        vocabulary = data["vocabulary"]
        assert "mastered_count" in vocabulary
        assert "biological_target" in vocabulary
        assert "mastery_percentage" in vocabulary
        assert "recent_mastered" in vocabulary
        
        assert isinstance(vocabulary["mastered_count"], (int, float))
        assert isinstance(vocabulary["biological_target"], (int, float))
        assert isinstance(vocabulary["mastery_percentage"], (int, float))
        assert isinstance(vocabulary["recent_mastered"], list)
        
        print(f"✓ Vocabulary data structure correct")
    
    def test_progress_assessments_structure(self, guardian_auth):
        """Test assessments data structure in progress response"""
        students_response = requests.get(
            f"{BASE_URL}/api/students",
            params={"guardian_id": guardian_auth["user"]["id"]},
            headers=guardian_auth["headers"]
        )
        assert students_response.status_code == 200
        students = students_response.json()
        
        if not students:
            pytest.skip("No students found for this guardian")
        
        student_id = students[0]["id"]
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/progress",
            headers=guardian_auth["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify assessments structure
        assessments = data["assessments"]
        assert "total" in assessments
        assert "completed" in assessments
        assert "average_accuracy" in assessments
        assert "history" in assessments
        
        assert isinstance(assessments["total"], (int, float))
        assert isinstance(assessments["completed"], (int, float))
        assert isinstance(assessments["average_accuracy"], (int, float))
        assert isinstance(assessments["history"], list)
        
        print(f"✓ Assessments data structure correct")
    
    def test_progress_narratives_structure(self, guardian_auth):
        """Test narratives data structure in progress response"""
        students_response = requests.get(
            f"{BASE_URL}/api/students",
            params={"guardian_id": guardian_auth["user"]["id"]},
            headers=guardian_auth["headers"]
        )
        assert students_response.status_code == 200
        students = students_response.json()
        
        if not students:
            pytest.skip("No students found for this guardian")
        
        student_id = students[0]["id"]
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/progress",
            headers=guardian_auth["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify narratives structure
        narratives = data["narratives"]
        assert "total" in narratives
        assert "completed" in narratives
        assert "stories" in narratives
        
        assert isinstance(narratives["total"], (int, float))
        assert isinstance(narratives["completed"], (int, float))
        assert isinstance(narratives["stories"], list)
        
        print(f"✓ Narratives data structure correct")


class TestProgressEmptyStates:
    """Test progress endpoint handles empty data gracefully"""
    
    @pytest.fixture
    def fresh_guardian_with_student(self):
        """Create a new guardian with a new student (no activity data)"""
        unique_id = str(uuid.uuid4())[:8]
        guardian_data = {
            "full_name": f"TEST_FreshGuardian_{unique_id}",
            "email": f"test_fresh_{unique_id}@example.com",
            "password": "TestPass123!",
            "role": "guardian"
        }
        
        # Register
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=guardian_data
        )
        if register_response.status_code != 200:
            pytest.skip(f"Cannot register fresh guardian: {register_response.status_code}")
        
        # Login
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": guardian_data["email"], "password": guardian_data["password"]}
        )
        if login_response.status_code != 200:
            pytest.skip(f"Cannot login as fresh guardian: {login_response.status_code}")
        
        auth_data = login_response.json()
        user = auth_data["user"]
        headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
        
        # Create a fresh student
        student_data = {
            "guardian_id": user["id"],
            "full_name": f"TEST_FreshStudent_{unique_id}",
            "age": 9,
            "grade_level": "1-12",
            "interests": ["games"],
            "virtues": ["patience"]
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/students",
            json=student_data,
            headers=headers
        )
        if create_response.status_code != 200:
            pytest.skip(f"Cannot create fresh student: {create_response.status_code}")
        
        student = create_response.json()
        
        return {
            "user": user,
            "headers": headers,
            "student": student
        }
    
    def test_progress_with_no_activity(self, fresh_guardian_with_student):
        """Test progress endpoint with a fresh student (no activity)"""
        student_id = fresh_guardian_with_student["student"]["id"]
        headers = fresh_guardian_with_student["headers"]
        
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/progress",
            headers=headers
        )
        
        assert response.status_code == 200, f"Failed to get progress: {response.status_code}"
        data = response.json()
        
        # Verify empty stats are returned correctly (not errors)
        assert data["reading_stats"]["total_reading_seconds"] == 0
        assert data["reading_stats"]["total_words_read"] == 0
        assert data["reading_stats"]["average_wpm"] == 0
        assert data["reading_stats"]["sessions_count"] == 0
        
        assert data["vocabulary"]["mastered_count"] == 0
        
        assert data["assessments"]["total"] == 0
        assert data["assessments"]["completed"] == 0
        assert data["assessments"]["history"] == []
        
        assert data["narratives"]["total"] == 0
        assert data["narratives"]["completed"] == 0
        assert data["narratives"]["stories"] == []
        
        print("✓ Progress endpoint handles empty data correctly")


class TestProgressEndpointNotFound:
    """Test progress endpoint with invalid student ID"""
    
    @pytest.fixture
    def guardian_auth(self):
        """Login as the test guardian"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_GUARDIAN_EMAIL, "password": TEST_GUARDIAN_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Cannot login as test guardian: {response.status_code}")
        
        data = response.json()
        return {"headers": {"Authorization": f"Bearer {data['access_token']}"}}
    
    def test_progress_nonexistent_student(self, guardian_auth):
        """Test progress endpoint with nonexistent student ID"""
        fake_student_id = "nonexistent-student-id-12345"
        response = requests.get(
            f"{BASE_URL}/api/students/{fake_student_id}/progress",
            headers=guardian_auth["headers"]
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Progress endpoint returns 404 for nonexistent student")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
