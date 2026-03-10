"""
Iteration 42: Parental Controls API Tests
Tests GET/PUT /api/students/{id}/parental-controls endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://audio-book-vault.preview.emergentagent.com')

# Test credentials
TEST_ADMIN_EMAIL = "allen@songsforcenturies.com"
TEST_ADMIN_PASSWORD = "LexiAdmin2026!"
TEST_STUDENT_ID_WITH_CONTROLS = "770d6413-0c3d-4149-9704-f709c89d9cc5"  # Alice - has controls set
TEST_STUDENT_ID_DEFAULT = "18316e14-9f7f-4960-9aba-e809fad104a2"  # SJ - test student


@pytest.fixture(scope="module")
def auth_token():
    """Get auth token for admin user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_ADMIN_EMAIL,
        "password": TEST_ADMIN_PASSWORD
    })
    assert response.status_code == 200
    return response.json()["access_token"]


class TestParentalControlsAPI:
    """Parental Controls GET/PUT endpoint tests"""
    
    def test_get_parental_controls_returns_defaults_or_saved(self, auth_token):
        """GET /api/students/{id}/parental-controls returns controls"""
        response = requests.get(
            f"{BASE_URL}/api/students/{TEST_STUDENT_ID_WITH_CONTROLS}/parental-controls",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should have all required fields
        assert "recording_mode" in data
        assert "chapter_threshold" in data
        assert "can_skip_recording" in data
        assert "auto_start_recording" in data
        assert "require_confirmation" in data
        
        # Validate types
        assert isinstance(data["recording_mode"], str)
        assert isinstance(data["chapter_threshold"], int)
        assert isinstance(data["can_skip_recording"], bool)
        
    def test_get_parental_controls_for_nonexistent_student(self, auth_token):
        """GET /api/students/{id}/parental-controls returns 404 for invalid student"""
        response = requests.get(
            f"{BASE_URL}/api/students/nonexistent-id/parental-controls",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404
        
    def test_put_parental_controls_saves_audio_required(self, auth_token):
        """PUT /api/students/{id}/parental-controls saves audio_required mode"""
        # Set to audio_required with specific settings
        new_controls = {
            "recording_mode": "audio_required",
            "auto_start_recording": False,
            "require_confirmation": True,
            "chapter_threshold": 2,
            "can_skip_recording": False
        }
        
        response = requests.put(
            f"{BASE_URL}/api/students/{TEST_STUDENT_ID_DEFAULT}/parental-controls",
            headers={"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"},
            json=new_controls
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify returned data matches
        assert data["recording_mode"] == "audio_required"
        assert data["chapter_threshold"] == 2
        assert data["can_skip_recording"] == False
        
        # Verify persistence with GET
        get_response = requests.get(
            f"{BASE_URL}/api/students/{TEST_STUDENT_ID_DEFAULT}/parental-controls",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data["recording_mode"] == "audio_required"
        assert get_data["chapter_threshold"] == 2
        assert get_data["can_skip_recording"] == False
        
    def test_put_parental_controls_video_required(self, auth_token):
        """PUT saves video_required mode"""
        new_controls = {
            "recording_mode": "video_required",
            "auto_start_recording": True,
            "require_confirmation": False,
            "chapter_threshold": 0,
            "can_skip_recording": True
        }
        
        response = requests.put(
            f"{BASE_URL}/api/students/{TEST_STUDENT_ID_DEFAULT}/parental-controls",
            headers={"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"},
            json=new_controls
        )
        assert response.status_code == 200
        data = response.json()
        assert data["recording_mode"] == "video_required"
        assert data["auto_start_recording"] == True
        
    def test_put_parental_controls_both_required(self, auth_token):
        """PUT saves both_required mode"""
        new_controls = {
            "recording_mode": "both_required",
            "auto_start_recording": False,
            "require_confirmation": True,
            "chapter_threshold": 3,
            "can_skip_recording": False
        }
        
        response = requests.put(
            f"{BASE_URL}/api/students/{TEST_STUDENT_ID_DEFAULT}/parental-controls",
            headers={"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"},
            json=new_controls
        )
        assert response.status_code == 200
        data = response.json()
        assert data["recording_mode"] == "both_required"
        assert data["chapter_threshold"] == 3
        
    def test_put_parental_controls_optional(self, auth_token):
        """PUT saves optional mode (resets to default behavior)"""
        new_controls = {
            "recording_mode": "optional",
            "auto_start_recording": False,
            "require_confirmation": True,
            "chapter_threshold": 0,
            "can_skip_recording": True
        }
        
        response = requests.put(
            f"{BASE_URL}/api/students/{TEST_STUDENT_ID_DEFAULT}/parental-controls",
            headers={"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"},
            json=new_controls
        )
        assert response.status_code == 200
        data = response.json()
        assert data["recording_mode"] == "optional"
        assert data["can_skip_recording"] == True


class TestBrutalComponentColors:
    """Test that softer color scheme data-testid attributes are present in API responses"""
    
    def test_students_endpoint_returns_valid_data(self, auth_token):
        """Verify students endpoint returns proper data structure"""
        response = requests.get(
            f"{BASE_URL}/api/students",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        students = response.json()
        assert isinstance(students, list)
        if students:
            student = students[0]
            assert "id" in student
            assert "full_name" in student
            assert "student_code" in student
            assert "access_pin" in student


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
