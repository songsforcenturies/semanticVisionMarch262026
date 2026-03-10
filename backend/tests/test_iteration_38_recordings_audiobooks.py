"""
Test Iteration 38: Read-Aloud Recording System and Audio Book Collection
Features tested:
- POST /api/recordings/upload - Upload recording (multipart form data)
- POST /api/recordings/{id}/analyze - Analyze recording with diction scoring
- GET /api/recordings/guardian/all - Get all recordings for guardian's students
- GET /api/recordings/student/{id}/progress - Get diction progress for student
- GET /api/audio-books - Get public audio book collection
- POST /api/audio-books/contribute - Contribute recording to audio books
- GET /api/admin/audio-books - Admin get all audio books
- PUT /api/admin/audio-books/settings - Admin update settings
"""

import pytest
import requests
import os
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"


class TestRecordingsAndAudioBooks:
    """Test suite for new recording and audio book features"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, admin_token):
        """Auth headers for requests"""
        return {"Authorization": f"Bearer {admin_token}"}
    
    @pytest.fixture(scope="class")
    def student_data(self, auth_headers):
        """Get a student ID for testing"""
        response = requests.get(f"{BASE_URL}/api/students", headers=auth_headers)
        assert response.status_code == 200
        students = response.json()
        if students:
            return students[0]
        return None
    
    # ==================== RECORDING UPLOAD ENDPOINT ====================
    
    def test_recording_upload_endpoint_exists(self, auth_headers, student_data):
        """Test POST /api/recordings/upload endpoint exists and validates"""
        if not student_data:
            pytest.skip("No student found for testing")
        
        # Try without file - should return 422 (validation error) or 400
        response = requests.post(
            f"{BASE_URL}/api/recordings/upload",
            headers=auth_headers,
            data={
                "student_id": student_data["id"],
                "narrative_id": "fake-narrative-id",
                "chapter_number": "1",
                "recording_type": "audio"
            }
        )
        # Endpoint exists - will return validation error for missing file (422) or 400/404
        assert response.status_code in [400, 404, 422], f"Unexpected status: {response.status_code}"
        print(f"Recording upload endpoint exists, returned {response.status_code}")
    
    def test_recording_upload_with_invalid_file_type(self, auth_headers, student_data):
        """Test that upload rejects invalid file types"""
        if not student_data:
            pytest.skip("No student found for testing")
        
        # Create a dummy text file
        fake_file = io.BytesIO(b"This is not an audio file")
        
        response = requests.post(
            f"{BASE_URL}/api/recordings/upload",
            headers=auth_headers,
            data={
                "student_id": student_data["id"],
                "narrative_id": "fake-narrative-id",
                "chapter_number": "1",
                "recording_type": "audio"
            },
            files={"file": ("test.txt", fake_file, "text/plain")}
        )
        # Should reject with 400 for unsupported file type or 404 for missing narrative
        assert response.status_code in [400, 404], f"Expected 400/404, got {response.status_code}"
        print(f"Invalid file type handled correctly: {response.status_code}")
    
    # ==================== RECORDING ANALYZE ENDPOINT ====================
    
    def test_recording_analyze_endpoint_exists(self, auth_headers):
        """Test POST /api/recordings/{id}/analyze endpoint exists"""
        # Test with fake recording ID - should return 404
        fake_id = "nonexistent-recording-id"
        response = requests.post(
            f"{BASE_URL}/api/recordings/{fake_id}/analyze",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Analyze endpoint exists and returns 404 for missing recording")
    
    # ==================== GUARDIAN RECORDINGS ENDPOINT ====================
    
    def test_guardian_recordings_endpoint(self, auth_headers):
        """Test GET /api/recordings/guardian/all returns recordings list"""
        response = requests.get(
            f"{BASE_URL}/api/recordings/guardian/all",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "recordings" in data, "Response should have 'recordings' key"
        assert "students" in data, "Response should have 'students' key"
        assert isinstance(data["recordings"], list), "recordings should be a list"
        assert isinstance(data["students"], list), "students should be a list"
        print(f"Guardian recordings endpoint works: {len(data['recordings'])} recordings, {len(data['students'])} students")
    
    # ==================== STUDENT DICTION PROGRESS ENDPOINT ====================
    
    def test_student_progress_endpoint(self, auth_headers, student_data):
        """Test GET /api/recordings/student/{id}/progress returns progress data"""
        if not student_data:
            pytest.skip("No student found for testing")
        
        response = requests.get(
            f"{BASE_URL}/api/recordings/student/{student_data['id']}/progress",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "progress" in data, "Response should have 'progress' key"
        assert "improvement" in data, "Response should have 'improvement' key"
        assert "total_sessions" in data, "Response should have 'total_sessions' key"
        assert isinstance(data["progress"], list), "progress should be a list"
        assert isinstance(data["total_sessions"], int), "total_sessions should be an int"
        print(f"Student progress endpoint works: {data['total_sessions']} sessions")
    
    # ==================== AUDIO BOOKS PUBLIC ENDPOINT ====================
    
    def test_audio_books_public_endpoint(self):
        """Test GET /api/audio-books returns collection (no auth required for public)"""
        response = requests.get(f"{BASE_URL}/api/audio-books")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "audio_books" in data, "Response should have 'audio_books' key"
        assert "total" in data, "Response should have 'total' key"
        assert "enabled" in data, "Response should have 'enabled' key"
        assert isinstance(data["audio_books"], list), "audio_books should be a list"
        print(f"Audio books endpoint works: {len(data['audio_books'])} books, enabled={data['enabled']}")
    
    def test_audio_books_pagination(self):
        """Test GET /api/audio-books supports pagination"""
        response = requests.get(f"{BASE_URL}/api/audio-books?page=1")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        response2 = requests.get(f"{BASE_URL}/api/audio-books?page=2")
        assert response2.status_code == 200, f"Page 2 failed: {response2.text}"
        print("Audio books pagination works")
    
    # ==================== AUDIO BOOKS CONTRIBUTE ENDPOINT ====================
    
    def test_audio_books_contribute_endpoint_exists(self, auth_headers):
        """Test POST /api/audio-books/contribute endpoint exists"""
        response = requests.post(
            f"{BASE_URL}/api/audio-books/contribute",
            headers=auth_headers,
            json={"recording_id": "fake-recording-id", "display_name": "Test Reader"}
        )
        # Should return 404 for nonexistent recording
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Audio books contribute endpoint exists")
    
    # ==================== ADMIN AUDIO BOOKS ENDPOINT ====================
    
    def test_admin_audio_books_endpoint(self, auth_headers):
        """Test GET /api/admin/audio-books returns all books (admin only)"""
        response = requests.get(
            f"{BASE_URL}/api/admin/audio-books",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "audio_books" in data, "Response should have 'audio_books' key"
        assert isinstance(data["audio_books"], list), "audio_books should be a list"
        print(f"Admin audio books endpoint works: {len(data['audio_books'])} books")
    
    def test_admin_audio_books_requires_auth(self):
        """Test GET /api/admin/audio-books requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/audio-books")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("Admin audio books endpoint correctly requires auth")
    
    # ==================== ADMIN AUDIO BOOK SETTINGS ====================
    
    def test_admin_audio_books_get_settings(self, auth_headers):
        """Test GET /api/admin/audio-books/settings returns settings"""
        response = requests.get(
            f"{BASE_URL}/api/admin/audio-books/settings",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify default settings structure
        assert isinstance(data, dict), "Settings should be a dict"
        print(f"Admin audio book settings: {data}")
    
    def test_admin_audio_books_update_settings(self, auth_headers):
        """Test PUT /api/admin/audio-books/settings saves settings"""
        # First get current settings
        get_response = requests.get(
            f"{BASE_URL}/api/admin/audio-books/settings",
            headers=auth_headers
        )
        current_settings = get_response.json()
        
        # Update settings
        new_settings = {
            "enabled": True,
            "auto_approve": False,
            "show_on_landing": True
        }
        
        response = requests.put(
            f"{BASE_URL}/api/admin/audio-books/settings",
            headers=auth_headers,
            json=new_settings
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        # Verify settings were saved
        verify_response = requests.get(
            f"{BASE_URL}/api/admin/audio-books/settings",
            headers=auth_headers
        )
        saved_settings = verify_response.json()
        assert saved_settings.get("enabled") == True, "enabled setting not saved"
        assert saved_settings.get("auto_approve") == False, "auto_approve setting not saved"
        print("Admin audio book settings update works")
    
    # ==================== STUDENT RECORDINGS ENDPOINT ====================
    
    def test_student_recordings_endpoint(self, auth_headers, student_data):
        """Test GET /api/recordings/student/{id} returns recordings"""
        if not student_data:
            pytest.skip("No student found for testing")
        
        response = requests.get(
            f"{BASE_URL}/api/recordings/student/{student_data['id']}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "recordings" in data, "Response should have 'recordings' key"
        assert isinstance(data["recordings"], list), "recordings should be a list"
        print(f"Student recordings endpoint works: {len(data['recordings'])} recordings")
    
    # ==================== ADMIN UPDATE AUDIO BOOK ====================
    
    def test_admin_update_audio_book_endpoint(self, auth_headers):
        """Test PUT /api/admin/audio-books/{id} endpoint exists"""
        fake_id = "nonexistent-book-id"
        response = requests.put(
            f"{BASE_URL}/api/admin/audio-books/{fake_id}",
            headers=auth_headers,
            json={"status": "approved", "is_visible": True}
        )
        # Should return 200 even for nonexistent ID (MongoDB update)
        # or could return success since update_one doesn't error on no match
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}"
        print(f"Admin update audio book endpoint exists: {response.status_code}")
    
    # ==================== ADMIN DELETE AUDIO BOOK ====================
    
    def test_admin_delete_audio_book_endpoint(self, auth_headers):
        """Test DELETE /api/admin/audio-books/{id} endpoint exists"""
        fake_id = "nonexistent-book-id"
        response = requests.delete(
            f"{BASE_URL}/api/admin/audio-books/{fake_id}",
            headers=auth_headers
        )
        # Should return 200 even for nonexistent ID (MongoDB delete)
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}"
        print(f"Admin delete audio book endpoint exists: {response.status_code}")


class TestAudioBooksLikeAndStream:
    """Test audio book like and stream endpoints"""
    
    def test_audio_book_like_endpoint(self):
        """Test POST /api/audio-books/{id}/like endpoint"""
        fake_id = "test-book-id"
        response = requests.post(f"{BASE_URL}/api/audio-books/{fake_id}/like")
        # Should return 200 (MongoDB update_one doesn't error on no match)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("Audio book like endpoint works")
    
    def test_audio_book_stream_endpoint(self):
        """Test GET /api/audio-books/{id}/stream endpoint exists"""
        fake_id = "nonexistent-book-id"
        response = requests.get(f"{BASE_URL}/api/audio-books/{fake_id}/stream")
        # Should return 404 for nonexistent book
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Audio book stream endpoint exists (returns 404 for missing)")


class TestRecordingStreamAndDelete:
    """Test recording stream and delete endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, admin_token):
        return {"Authorization": f"Bearer {admin_token}"}
    
    def test_recording_stream_endpoint(self):
        """Test GET /api/recordings/{id}/stream endpoint exists"""
        fake_id = "nonexistent-recording-id"
        response = requests.get(f"{BASE_URL}/api/recordings/{fake_id}/stream")
        # Should return 404 for nonexistent recording
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Recording stream endpoint exists (returns 404 for missing)")
    
    def test_recording_delete_endpoint(self, auth_headers):
        """Test DELETE /api/recordings/{id} endpoint exists"""
        fake_id = "nonexistent-recording-id"
        response = requests.delete(
            f"{BASE_URL}/api/recordings/{fake_id}",
            headers=auth_headers
        )
        # Should return 404 for nonexistent recording
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Recording delete endpoint exists (returns 404 for missing)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
