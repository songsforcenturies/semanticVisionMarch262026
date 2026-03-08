"""
Iteration 27: Student Strengths & Weaknesses Feature Tests
- Student model includes 'strengths' and 'weaknesses' string fields
- POST /api/students creates a student with strengths and weaknesses fields
- PUT /api/students/{id} updates strengths and weaknesses fields
- GET /api/students/{id} returns strengths and weaknesses in the response
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
GUARDIAN_EMAIL = "allen@ourfamily.contact"
GUARDIAN_PASSWORD = "LexiAdmin2026!"
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"

@pytest.fixture(scope="module")
def guardian_auth():
    """Get guardian auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": GUARDIAN_EMAIL,
        "password": GUARDIAN_PASSWORD
    })
    assert response.status_code == 200, f"Guardian login failed: {response.text}"
    data = response.json()
    return {
        "token": data["access_token"],
        "user_id": data["user"]["id"],
        "headers": {"Authorization": f"Bearer {data['access_token']}"}
    }

@pytest.fixture(scope="module")
def admin_auth():
    """Get admin auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    data = response.json()
    return {
        "token": data["access_token"],
        "user_id": data["user"]["id"],
        "headers": {"Authorization": f"Bearer {data['access_token']}"}
    }


class TestStudentStrengthsWeaknesses:
    """Tests for student strengths and weaknesses fields"""
    
    created_student_id = None
    
    def test_create_student_with_strengths_weaknesses(self, guardian_auth):
        """POST /api/students creates student with strengths and weaknesses"""
        payload = {
            "full_name": "TEST_Strengths_Student_27",
            "guardian_id": guardian_auth["user_id"],
            "age": 10,
            "grade_level": "1-12",
            "interests": ["science", "reading"],
            "strengths": "Very creative and imaginative. Great at math. Natural leader among friends.",
            "weaknesses": "Struggles with patience. Gets frustrated easily with hard tasks."
        }
        
        response = requests.post(
            f"{BASE_URL}/api/students",
            json=payload,
            headers=guardian_auth["headers"]
        )
        
        assert response.status_code == 200, f"Create student failed: {response.text}"
        data = response.json()
        
        # Store for cleanup
        TestStudentStrengthsWeaknesses.created_student_id = data["id"]
        
        # Verify strengths and weaknesses are in response
        assert "strengths" in data, "Response missing 'strengths' field"
        assert "weaknesses" in data, "Response missing 'weaknesses' field"
        assert data["strengths"] == payload["strengths"], f"Strengths mismatch: expected '{payload['strengths']}', got '{data['strengths']}'"
        assert data["weaknesses"] == payload["weaknesses"], f"Weaknesses mismatch: expected '{payload['weaknesses']}', got '{data['weaknesses']}'"
        print(f"✓ Created student with strengths: '{data['strengths'][:50]}...'")
        print(f"✓ Created student with weaknesses: '{data['weaknesses'][:50]}...'")
    
    def test_get_student_returns_strengths_weaknesses(self, guardian_auth):
        """GET /api/students/{id} returns strengths and weaknesses"""
        student_id = TestStudentStrengthsWeaknesses.created_student_id
        assert student_id, "No student created yet"
        
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}",
            headers=guardian_auth["headers"]
        )
        
        assert response.status_code == 200, f"Get student failed: {response.text}"
        data = response.json()
        
        # Verify fields are present
        assert "strengths" in data, "GET response missing 'strengths' field"
        assert "weaknesses" in data, "GET response missing 'weaknesses' field"
        assert len(data["strengths"]) > 0, "Strengths should not be empty"
        assert len(data["weaknesses"]) > 0, "Weaknesses should not be empty"
        print(f"✓ GET returned strengths: '{data['strengths'][:50]}...'")
        print(f"✓ GET returned weaknesses: '{data['weaknesses'][:50]}...'")
    
    def test_update_student_strengths_weaknesses(self, guardian_auth):
        """PUT /api/students/{id} updates strengths and weaknesses"""
        student_id = TestStudentStrengthsWeaknesses.created_student_id
        assert student_id, "No student created yet"
        
        new_strengths = "Updated: Excellent at storytelling. Very empathetic toward others."
        new_weaknesses = "Updated: Needs help with time management. Works on sharing."
        
        response = requests.patch(
            f"{BASE_URL}/api/students/{student_id}",
            json={
                "strengths": new_strengths,
                "weaknesses": new_weaknesses
            },
            headers=guardian_auth["headers"]
        )
        
        assert response.status_code == 200, f"Update student failed: {response.text}"
        data = response.json()
        
        assert data["strengths"] == new_strengths, f"Strengths not updated: got '{data['strengths']}'"
        assert data["weaknesses"] == new_weaknesses, f"Weaknesses not updated: got '{data['weaknesses']}'"
        print(f"✓ Updated strengths: '{data['strengths'][:50]}...'")
        print(f"✓ Updated weaknesses: '{data['weaknesses'][:50]}...'")
    
    def test_create_student_with_empty_strengths_weaknesses(self, guardian_auth):
        """POST /api/students allows empty strengths and weaknesses"""
        payload = {
            "full_name": "TEST_Empty_Fields_Student_27",
            "guardian_id": guardian_auth["user_id"],
            "age": 8,
            "grade_level": "1-12",
            "interests": ["art"],
            # No strengths or weaknesses - should default to empty strings
        }
        
        response = requests.post(
            f"{BASE_URL}/api/students",
            json=payload,
            headers=guardian_auth["headers"]
        )
        
        assert response.status_code == 200, f"Create student failed: {response.text}"
        data = response.json()
        
        # Verify fields exist and are empty strings
        assert "strengths" in data, "Response missing 'strengths' field"
        assert "weaknesses" in data, "Response missing 'weaknesses' field"
        assert data["strengths"] == "", "Strengths should default to empty string"
        assert data["weaknesses"] == "", "Weaknesses should default to empty string"
        
        # Cleanup - delete this student
        requests.delete(f"{BASE_URL}/api/students/{data['id']}", headers=guardian_auth["headers"])
        print("✓ Empty strengths/weaknesses default to empty strings")
    
    def test_update_student_clear_strengths_weaknesses(self, guardian_auth):
        """PUT /api/students/{id} can clear strengths and weaknesses"""
        student_id = TestStudentStrengthsWeaknesses.created_student_id
        assert student_id, "No student created yet"
        
        response = requests.patch(
            f"{BASE_URL}/api/students/{student_id}",
            json={
                "strengths": "",
                "weaknesses": ""
            },
            headers=guardian_auth["headers"]
        )
        
        assert response.status_code == 200, f"Update student failed: {response.text}"
        data = response.json()
        
        assert data["strengths"] == "", "Strengths should be cleared"
        assert data["weaknesses"] == "", "Weaknesses should be cleared"
        print("✓ Can clear strengths/weaknesses to empty strings")
    
    def test_list_students_includes_strengths_weaknesses(self, guardian_auth):
        """GET /api/students returns strengths and weaknesses in list"""
        response = requests.get(
            f"{BASE_URL}/api/students",
            params={"guardian_id": guardian_auth["user_id"]},
            headers=guardian_auth["headers"]
        )
        
        assert response.status_code == 200, f"List students failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Response should be a list"
        if len(data) > 0:
            # Check that at least one student has the fields
            for student in data:
                assert "strengths" in student, f"Student {student.get('id')} missing 'strengths' field"
                assert "weaknesses" in student, f"Student {student.get('id')} missing 'weaknesses' field"
            print(f"✓ All {len(data)} students have strengths/weaknesses fields")
    
    def test_cleanup_test_student(self, guardian_auth):
        """Clean up test student created during tests"""
        student_id = TestStudentStrengthsWeaknesses.created_student_id
        if student_id:
            response = requests.delete(
                f"{BASE_URL}/api/students/{student_id}",
                headers=guardian_auth["headers"]
            )
            assert response.status_code == 200, f"Delete student failed: {response.text}"
            print(f"✓ Cleaned up test student: {student_id}")


class TestStudentModelFields:
    """Tests to verify Student model structure includes strengths/weaknesses"""
    
    def test_existing_student_has_fields(self, guardian_auth):
        """Verify existing students have strengths/weaknesses fields"""
        response = requests.get(
            f"{BASE_URL}/api/students",
            params={"guardian_id": guardian_auth["user_id"]},
            headers=guardian_auth["headers"]
        )
        
        assert response.status_code == 200
        students = response.json()
        
        if len(students) > 0:
            student = students[0]
            # Fields should exist (even if empty)
            assert "strengths" in student, "Existing student missing 'strengths' field"
            assert "weaknesses" in student, "Existing student missing 'weaknesses' field"
            print(f"✓ Existing student '{student['full_name']}' has strengths/weaknesses fields")
        else:
            pytest.skip("No existing students to test")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
