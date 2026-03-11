"""
Test Suite for Iteration 49: Digital Media Features
- Admin Digital Media management (settings, brand media CRUD)
- Guardian children media controls
- Student media library
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://learning-portal-v1.preview.emergentagent.com')

class TestAdminMediaSettings:
    """Admin media settings endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "allen@songsforcenturies.com",
            "password": "LexiAdmin2026!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_media_settings(self):
        """Test GET /api/admin/media-settings"""
        response = requests.get(f"{BASE_URL}/api/admin/media-settings", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify expected fields exist
        assert "digital_media_enabled" in data
        assert "default_price_per_stream" in data
        assert "default_price_per_download" in data
        
        # Verify data types
        assert isinstance(data["digital_media_enabled"], bool)
        assert isinstance(data["default_price_per_stream"], (int, float))
        assert isinstance(data["default_price_per_download"], (int, float))
        print(f"Media settings: enabled={data['digital_media_enabled']}, stream=${data['default_price_per_stream']}, download=${data['default_price_per_download']}")
    
    def test_update_media_settings_toggle(self):
        """Test PUT /api/admin/media-settings - toggle digital_media_enabled"""
        # Get current state
        get_response = requests.get(f"{BASE_URL}/api/admin/media-settings", headers=self.headers)
        original_state = get_response.json()["digital_media_enabled"]
        
        # Toggle state
        response = requests.put(f"{BASE_URL}/api/admin/media-settings", 
            headers=self.headers,
            json={"digital_media_enabled": not original_state})
        assert response.status_code == 200
        assert response.json()["message"] == "Media settings updated"
        
        # Verify toggle persisted
        verify_response = requests.get(f"{BASE_URL}/api/admin/media-settings", headers=self.headers)
        assert verify_response.json()["digital_media_enabled"] == (not original_state)
        
        # Restore original state
        requests.put(f"{BASE_URL}/api/admin/media-settings", 
            headers=self.headers,
            json={"digital_media_enabled": original_state})
        print(f"Toggle test passed: {original_state} -> {not original_state} -> {original_state}")
    
    def test_update_media_settings_pricing(self):
        """Test PUT /api/admin/media-settings - update pricing"""
        response = requests.put(f"{BASE_URL}/api/admin/media-settings",
            headers=self.headers,
            json={"default_price_per_stream": 0.05, "default_price_per_download": 1.99})
        assert response.status_code == 200
        
        # Verify update
        verify = requests.get(f"{BASE_URL}/api/admin/media-settings", headers=self.headers)
        data = verify.json()
        assert data["default_price_per_stream"] == 0.05
        assert data["default_price_per_download"] == 1.99
        
        # Reset to defaults
        requests.put(f"{BASE_URL}/api/admin/media-settings",
            headers=self.headers,
            json={"default_price_per_stream": 0, "default_price_per_download": 0.99})
        print("Pricing update test passed")


class TestAdminBrandMedia:
    """Admin brand media CRUD tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "allen@songsforcenturies.com",
            "password": "LexiAdmin2026!"
        })
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_list_brand_media(self):
        """Test GET /api/admin/brand-media"""
        response = requests.get(f"{BASE_URL}/api/admin/brand-media", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"Found {len(data)} brand media items")
        
        if len(data) > 0:
            item = data[0]
            # Verify structure
            assert "id" in item
            assert "title" in item
            assert "artist" in item
            assert "media_type" in item
            assert "status" in item
    
    def test_create_youtube_video(self):
        """Test POST /api/admin/brand-media - create YouTube video"""
        test_id = uuid.uuid4().hex[:8]
        payload = {
            "title": f"TEST_Video_{test_id}",
            "artist": f"TEST_Artist_{test_id}",
            "youtube_url": "https://www.youtube.com/watch?v=test123",
            "media_type": "video",
            "price_per_stream": 0.0,
            "price_per_download": 0.99
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/brand-media",
            headers=self.headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify created data
        assert data["title"] == payload["title"]
        assert data["artist"] == payload["artist"]
        assert data["youtube_url"] == payload["youtube_url"]
        assert data["media_type"] == "video"
        assert data["source"] == "youtube"
        assert data["status"] == "approved"
        assert "id" in data
        
        created_id = data["id"]
        print(f"Created YouTube video: {created_id}")
        
        # Verify persistence
        list_response = requests.get(f"{BASE_URL}/api/admin/brand-media", headers=self.headers)
        media_list = list_response.json()
        found = any(m["id"] == created_id for m in media_list)
        assert found, "Created video not found in list"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/admin/brand-media/{created_id}", headers=self.headers)
        print("YouTube video create test passed")
    
    def test_update_brand_media(self):
        """Test PUT /api/admin/brand-media/{id}"""
        # First create a test item
        test_id = uuid.uuid4().hex[:8]
        create_response = requests.post(f"{BASE_URL}/api/admin/brand-media",
            headers=self.headers,
            json={
                "title": f"TEST_UpdateMedia_{test_id}",
                "artist": "Original Artist",
                "youtube_url": "https://www.youtube.com/watch?v=update123",
                "media_type": "video"
            })
        assert create_response.status_code == 200
        media_id = create_response.json()["id"]
        
        # Update it
        update_response = requests.put(f"{BASE_URL}/api/admin/brand-media/{media_id}",
            headers=self.headers,
            json={"title": f"UPDATED_Title_{test_id}", "price_per_download": 2.99})
        assert update_response.status_code == 200
        assert update_response.json()["message"] == "Media updated"
        
        # Verify update
        list_response = requests.get(f"{BASE_URL}/api/admin/brand-media", headers=self.headers)
        media_list = list_response.json()
        updated_item = next((m for m in media_list if m["id"] == media_id), None)
        assert updated_item is not None
        assert updated_item["title"] == f"UPDATED_Title_{test_id}"
        assert updated_item["price_per_download"] == 2.99
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/admin/brand-media/{media_id}", headers=self.headers)
        print("Media update test passed")
    
    def test_delete_brand_media(self):
        """Test DELETE /api/admin/brand-media/{id}"""
        # First create a test item
        test_id = uuid.uuid4().hex[:8]
        create_response = requests.post(f"{BASE_URL}/api/admin/brand-media",
            headers=self.headers,
            json={
                "title": f"TEST_DeleteMedia_{test_id}",
                "artist": "Delete Artist",
                "youtube_url": "https://www.youtube.com/watch?v=delete123",
                "media_type": "video"
            })
        assert create_response.status_code == 200
        media_id = create_response.json()["id"]
        
        # Delete it
        delete_response = requests.delete(f"{BASE_URL}/api/admin/brand-media/{media_id}",
            headers=self.headers)
        assert delete_response.status_code == 200
        assert delete_response.json()["message"] == "Media deleted"
        
        # Verify deletion
        list_response = requests.get(f"{BASE_URL}/api/admin/brand-media", headers=self.headers)
        media_list = list_response.json()
        found = any(m["id"] == media_id for m in media_list)
        assert not found, "Deleted media still found in list"
        print("Media delete test passed")


class TestGuardianMediaFeatures:
    """Guardian media control tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get guardian token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "allen@songsforcenturies.com",
            "password": "LexiAdmin2026!"
        })
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_children_media(self):
        """Test GET /api/guardian/children-media"""
        response = requests.get(f"{BASE_URL}/api/guardian/children-media", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"Guardian has {len(data)} children media history items")
        
        # If there are items, verify structure
        if len(data) > 0:
            item = data[0]
            assert "student_id" in item
            assert "media_id" in item
            assert "title" in item
    
    def test_update_student_media_preference(self):
        """Test POST /api/students/{id}/media-preference"""
        # Get first student
        students_response = requests.get(f"{BASE_URL}/api/students", headers=self.headers)
        students = students_response.json()
        
        if len(students) == 0:
            pytest.skip("No students found to test media preference")
        
        student_id = students[0]["id"]
        student_name = students[0]["full_name"]
        
        # Toggle off
        off_response = requests.post(
            f"{BASE_URL}/api/students/{student_id}/media-preference?enabled=false",
            headers=self.headers)
        assert off_response.status_code == 200
        assert off_response.json()["enabled"] == False
        
        # Toggle on
        on_response = requests.post(
            f"{BASE_URL}/api/students/{student_id}/media-preference?enabled=true",
            headers=self.headers)
        assert on_response.status_code == 200
        assert on_response.json()["enabled"] == True
        
        print(f"Media preference toggle test passed for {student_name}")


class TestStudentMediaLibrary:
    """Student media library tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "allen@songsforcenturies.com",
            "password": "LexiAdmin2026!"
        })
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Get first student
        students_response = requests.get(f"{BASE_URL}/api/students", headers=self.headers)
        students = students_response.json()
        if len(students) > 0:
            self.student_id = students[0]["id"]
            self.student_name = students[0]["full_name"]
        else:
            self.student_id = None
    
    def test_get_student_media_library(self):
        """Test GET /api/students/{id}/media-library"""
        if not self.student_id:
            pytest.skip("No student found")
        
        response = requests.get(f"{BASE_URL}/api/students/{self.student_id}/media-library",
            headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"Student {self.student_name} has {len(data)} items in media library")
    
    def test_get_media_for_story(self):
        """Test GET /api/brand-media/for-story/{student_id}"""
        if not self.student_id:
            pytest.skip("No student found")
        
        response = requests.get(f"{BASE_URL}/api/brand-media/for-story/{self.student_id}",
            headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "media" in data
        if "reason" in data and data["reason"]:
            print(f"Media for story: {data['reason']}")
        else:
            print(f"Found {len(data['media'])} media items available for stories")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
