"""
Export Student Data API Tests
- GET /api/students/{id}/export?format=json (JSON download with Content-Disposition header)
- GET /api/students/{id}/export?format=html (styled HTML report)
- Guardian authentication and authorization for exports
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_GUARDIAN_EMAIL = "testreset@test.com"
TEST_GUARDIAN_PASSWORD = "Test1234!"
TEST_STUDENT_ID = "d32c8a5e-9734-4e8f-8b38-f33a3210d5e8"  # PinTest Kid


class TestExportAuthentication:
    """Test authentication and authorization for export endpoint"""
    
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
            "full_name": f"TEST_ExportOtherGuardian_{unique_id}",
            "email": f"test_export_other_{unique_id}@example.com",
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
    
    def test_export_requires_authentication(self):
        """Export endpoint returns 401 without authentication token"""
        response = requests.get(f"{BASE_URL}/api/students/{TEST_STUDENT_ID}/export?format=json")
        assert response.status_code in [401, 403], f"Expected 401/403 for no auth, got {response.status_code}"
        print("✓ Export endpoint requires authentication (returns 401/403 without token)")
    
    def test_export_rejects_unauthorized_guardian(self, guardian_auth, other_guardian_auth):
        """Export endpoint rejects unauthorized guardian (returns 403)"""
        # First verify test student belongs to test guardian
        response = requests.get(
            f"{BASE_URL}/api/students/{TEST_STUDENT_ID}/export?format=json",
            headers=guardian_auth["headers"]
        )
        
        if response.status_code == 200:
            # Now try with other guardian
            other_response = requests.get(
                f"{BASE_URL}/api/students/{TEST_STUDENT_ID}/export?format=json",
                headers=other_guardian_auth["headers"]
            )
            assert other_response.status_code == 403, f"Expected 403 Forbidden, got {other_response.status_code}"
            print("✓ Export endpoint rejects unauthorized guardian (returns 403)")
        else:
            pytest.skip(f"Test student not found or inaccessible: {response.status_code}")


class TestJSONExport:
    """Test JSON export format and content"""
    
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
    def get_student_for_export(self, guardian_auth):
        """Get or create a student for export testing"""
        # Try with TEST_STUDENT_ID first
        response = requests.get(
            f"{BASE_URL}/api/students/{TEST_STUDENT_ID}/export?format=json",
            headers=guardian_auth["headers"]
        )
        
        if response.status_code == 200:
            return TEST_STUDENT_ID, guardian_auth
        
        # Fallback: get first student for this guardian
        students_response = requests.get(
            f"{BASE_URL}/api/students",
            params={"guardian_id": guardian_auth["user"]["id"]},
            headers=guardian_auth["headers"]
        )
        
        if students_response.status_code == 200 and students_response.json():
            return students_response.json()[0]["id"], guardian_auth
        
        # Create a student if none exist
        unique_id = str(uuid.uuid4())[:8]
        student_data = {
            "guardian_id": guardian_auth["user"]["id"],
            "full_name": f"TEST_ExportStudent_{unique_id}",
            "age": 10,
            "grade_level": "1-12",
            "interests": ["reading"],
            "virtues": ["curiosity"]
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/students",
            json=student_data,
            headers=guardian_auth["headers"]
        )
        
        if create_response.status_code == 200:
            return create_response.json()["id"], guardian_auth
        
        pytest.skip("Cannot find or create a student for export testing")
    
    def test_json_export_status_code(self, get_student_for_export):
        """JSON export returns 200 status code"""
        student_id, auth = get_student_for_export
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/export?format=json",
            headers=auth["headers"]
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ JSON export returns 200")
    
    def test_json_export_content_disposition_header(self, get_student_for_export):
        """JSON export includes Content-Disposition header for file download"""
        student_id, auth = get_student_for_export
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/export?format=json",
            headers=auth["headers"]
        )
        assert response.status_code == 200
        
        content_disposition = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disposition, f"Expected 'attachment' in Content-Disposition, got: {content_disposition}"
        assert "filename=" in content_disposition, f"Expected 'filename=' in Content-Disposition, got: {content_disposition}"
        assert ".json" in content_disposition, f"Expected '.json' in filename, got: {content_disposition}"
        print(f"✓ JSON export has Content-Disposition header: {content_disposition}")
    
    def test_json_export_content_type(self, get_student_for_export):
        """JSON export returns application/json content type"""
        student_id, auth = get_student_for_export
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/export?format=json",
            headers=auth["headers"]
        )
        assert response.status_code == 200
        
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type, f"Expected 'application/json', got: {content_type}"
        print(f"✓ JSON export content type: {content_type}")
    
    def test_json_export_includes_report_date(self, get_student_for_export):
        """JSON export includes report_date field"""
        student_id, auth = get_student_for_export
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/export?format=json",
            headers=auth["headers"]
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "report_date" in data, "Missing 'report_date' in JSON export"
        assert len(data["report_date"]) > 0, "report_date should not be empty"
        print(f"✓ JSON export includes report_date: {data['report_date']}")
    
    def test_json_export_includes_exported_by(self, get_student_for_export):
        """JSON export includes exported_by field"""
        student_id, auth = get_student_for_export
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/export?format=json",
            headers=auth["headers"]
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "exported_by" in data, "Missing 'exported_by' in JSON export"
        print(f"✓ JSON export includes exported_by: {data['exported_by']}")
    
    def test_json_export_all_sections(self, get_student_for_export):
        """JSON export includes all required sections"""
        student_id, auth = get_student_for_export
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/export?format=json",
            headers=auth["headers"]
        )
        assert response.status_code == 200
        
        data = response.json()
        
        # Check all required sections
        required_sections = [
            "report_date",
            "exported_by", 
            "student",
            "reading_stats",
            "vocabulary",
            "assessments",
            "narratives",
            "assigned_banks"
        ]
        
        for section in required_sections:
            assert section in data, f"Missing '{section}' in JSON export"
        
        print(f"✓ JSON export includes all sections: {', '.join(required_sections)}")
    
    def test_json_export_student_profile(self, get_student_for_export):
        """JSON export student section contains profile info"""
        student_id, auth = get_student_for_export
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/export?format=json",
            headers=auth["headers"]
        )
        assert response.status_code == 200
        
        data = response.json()
        student = data.get("student", {})
        
        # Verify student profile fields
        assert "id" in student
        assert "full_name" in student
        assert "biological_target" in student
        
        print(f"✓ JSON export student profile: {student.get('full_name')}")


class TestHTMLExport:
    """Test HTML export format and content"""
    
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
    def get_student_for_export(self, guardian_auth):
        """Get or create a student for export testing"""
        # Try with TEST_STUDENT_ID first
        response = requests.get(
            f"{BASE_URL}/api/students/{TEST_STUDENT_ID}/export?format=html",
            headers=guardian_auth["headers"]
        )
        
        if response.status_code == 200:
            return TEST_STUDENT_ID, guardian_auth
        
        # Fallback: get first student for this guardian
        students_response = requests.get(
            f"{BASE_URL}/api/students",
            params={"guardian_id": guardian_auth["user"]["id"]},
            headers=guardian_auth["headers"]
        )
        
        if students_response.status_code == 200 and students_response.json():
            return students_response.json()[0]["id"], guardian_auth
        
        # Create a student if none exist
        unique_id = str(uuid.uuid4())[:8]
        student_data = {
            "guardian_id": guardian_auth["user"]["id"],
            "full_name": f"TEST_ExportStudent_{unique_id}",
            "age": 10,
            "grade_level": "1-12",
            "interests": ["reading"],
            "virtues": ["curiosity"]
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/students",
            json=student_data,
            headers=guardian_auth["headers"]
        )
        
        if create_response.status_code == 200:
            return create_response.json()["id"], guardian_auth
        
        pytest.skip("Cannot find or create a student for export testing")
    
    def test_html_export_status_code(self, get_student_for_export):
        """HTML export returns 200 status code"""
        student_id, auth = get_student_for_export
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/export?format=html",
            headers=auth["headers"]
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ HTML export returns 200")
    
    def test_html_export_content_type(self, get_student_for_export):
        """HTML export returns text/html content type"""
        student_id, auth = get_student_for_export
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/export?format=html",
            headers=auth["headers"]
        )
        assert response.status_code == 200
        
        content_type = response.headers.get("Content-Type", "")
        assert "text/html" in content_type, f"Expected 'text/html', got: {content_type}"
        print(f"✓ HTML export content type: {content_type}")
    
    def test_html_export_is_valid_html(self, get_student_for_export):
        """HTML export returns valid HTML document"""
        student_id, auth = get_student_for_export
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/export?format=html",
            headers=auth["headers"]
        )
        assert response.status_code == 200
        
        html_content = response.text
        
        # Check for basic HTML structure
        assert "<!DOCTYPE html>" in html_content, "Missing DOCTYPE"
        assert "<html" in html_content, "Missing <html> tag"
        assert "</html>" in html_content, "Missing </html> tag"
        assert "<head>" in html_content, "Missing <head> tag"
        assert "<body>" in html_content, "Missing <body> tag"
        
        print("✓ HTML export is valid HTML document")
    
    def test_html_export_contains_student_name(self, get_student_for_export):
        """HTML export contains student name"""
        student_id, auth = get_student_for_export
        
        # First get student name
        student_response = requests.get(
            f"{BASE_URL}/api/students/{student_id}",
            headers=auth["headers"]
        )
        student_name = ""
        if student_response.status_code == 200:
            student_name = student_response.json().get("full_name", "")
        
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/export?format=html",
            headers=auth["headers"]
        )
        assert response.status_code == 200
        
        html_content = response.text
        
        # Student name should appear in HTML
        if student_name:
            assert student_name in html_content, f"Student name '{student_name}' not found in HTML"
            print(f"✓ HTML export contains student name: {student_name}")
        else:
            # Fallback: check for generic student info markers
            assert "Student Profile" in html_content or "LexiMaster Report" in html_content
            print("✓ HTML export contains student profile section")
    
    def test_html_export_contains_stats_grid(self, get_student_for_export):
        """HTML export contains stats grid section"""
        student_id, auth = get_student_for_export
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/export?format=html",
            headers=auth["headers"]
        )
        assert response.status_code == 200
        
        html_content = response.text
        
        # Check for stats-grid or stat boxes
        assert "stats-grid" in html_content or "stat-box" in html_content, "Missing stats grid in HTML"
        print("✓ HTML export contains stats grid")
    
    def test_html_export_contains_assessment_table(self, get_student_for_export):
        """HTML export contains assessment history table"""
        student_id, auth = get_student_for_export
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/export?format=html",
            headers=auth["headers"]
        )
        assert response.status_code == 200
        
        html_content = response.text
        
        # Check for assessment history section
        assert "Assessment History" in html_content, "Missing Assessment History section"
        assert "<table>" in html_content or "<table" in html_content, "Missing table element"
        print("✓ HTML export contains assessment history table")
    
    def test_html_export_contains_story_table(self, get_student_for_export):
        """HTML export contains story history table"""
        student_id, auth = get_student_for_export
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/export?format=html",
            headers=auth["headers"]
        )
        assert response.status_code == 200
        
        html_content = response.text
        
        # Check for story history section
        assert "Story History" in html_content, "Missing Story History section"
        print("✓ HTML export contains story history table")
    
    def test_html_export_contains_print_button(self, get_student_for_export):
        """HTML export contains Print / Save as PDF button"""
        student_id, auth = get_student_for_export
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/export?format=html",
            headers=auth["headers"]
        )
        assert response.status_code == 200
        
        html_content = response.text
        
        # Check for print button
        assert "Print" in html_content or "print" in html_content, "Missing print button"
        assert "window.print()" in html_content, "Missing print functionality"
        print("✓ HTML export contains print button with window.print()")
    
    def test_html_export_contains_print_styles(self, get_student_for_export):
        """HTML export contains @media print styles"""
        student_id, auth = get_student_for_export
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/export?format=html",
            headers=auth["headers"]
        )
        assert response.status_code == 200
        
        html_content = response.text
        
        # Check for print media query
        assert "@media print" in html_content, "Missing @media print styles"
        print("✓ HTML export contains @media print styles")


class TestExportEdgeCases:
    """Test export endpoint edge cases"""
    
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
    
    def test_export_nonexistent_student(self, guardian_auth):
        """Export endpoint returns 404 for nonexistent student"""
        fake_student_id = "nonexistent-export-student-12345"
        response = requests.get(
            f"{BASE_URL}/api/students/{fake_student_id}/export?format=json",
            headers=guardian_auth["headers"]
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Export returns 404 for nonexistent student")
    
    def test_export_default_format_is_json(self, guardian_auth):
        """Export endpoint defaults to JSON format when no format param"""
        # Get a valid student first
        students_response = requests.get(
            f"{BASE_URL}/api/students",
            params={"guardian_id": guardian_auth["user"]["id"]},
            headers=guardian_auth["headers"]
        )
        
        if students_response.status_code != 200 or not students_response.json():
            pytest.skip("No students found for guardian")
        
        student_id = students_response.json()[0]["id"]
        
        # Call export without format param
        response = requests.get(
            f"{BASE_URL}/api/students/{student_id}/export",
            headers=guardian_auth["headers"]
        )
        
        assert response.status_code == 200
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type, f"Expected JSON default, got: {content_type}"
        print("✓ Export defaults to JSON format")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
