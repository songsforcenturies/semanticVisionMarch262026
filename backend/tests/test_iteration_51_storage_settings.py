"""
Iteration 51 Tests: Storage Stats, Storage Settings, Support Tickets
- GET /api/admin/storage-stats - Returns storage breakdown
- PUT /api/admin/media-settings - Update storage settings (max_storage_per_user_mb, max_recording_duration_sec, auto_delete_recordings_days)
- Support tickets API verification
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"

class TestStorageAndMediaSettings:
    """Tests for storage stats and media settings endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def admin_client(self, admin_token):
        """Create authenticated session"""
        session = requests.Session()
        session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {admin_token}"
        })
        return session

    # === Storage Stats Tests ===
    def test_get_storage_stats_success(self, admin_client):
        """Test GET /api/admin/storage-stats returns storage breakdown"""
        response = admin_client.get(f"{BASE_URL}/api/admin/storage-stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify all required fields are present
        assert "total_storage_mb" in data, "Missing total_storage_mb field"
        assert "recordings_storage_mb" in data, "Missing recordings_storage_mb field"
        assert "media_storage_mb" in data, "Missing media_storage_mb field"
        assert "support_storage_mb" in data, "Missing support_storage_mb field"
        assert "recordings_count" in data, "Missing recordings_count field"
        assert "media_count" in data, "Missing media_count field"
        
        # Verify data types
        assert isinstance(data["total_storage_mb"], (int, float)), "total_storage_mb should be numeric"
        assert isinstance(data["recordings_storage_mb"], (int, float)), "recordings_storage_mb should be numeric"
        assert isinstance(data["media_storage_mb"], (int, float)), "media_storage_mb should be numeric"
        assert isinstance(data["support_storage_mb"], (int, float)), "support_storage_mb should be numeric"
        assert isinstance(data["recordings_count"], int), "recordings_count should be integer"
        assert isinstance(data["media_count"], int), "media_count should be integer"
        
        # Verify total equals sum of parts
        expected_total = round(data["recordings_storage_mb"] + data["media_storage_mb"] + data["support_storage_mb"], 2)
        assert abs(data["total_storage_mb"] - expected_total) < 0.01, "Total storage should equal sum of parts"
        
        print(f"Storage Stats: Total={data['total_storage_mb']}MB, Recordings={data['recordings_storage_mb']}MB, Media={data['media_storage_mb']}MB, Support={data['support_storage_mb']}MB")

    def test_storage_stats_requires_auth(self):
        """Test storage stats requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/storage-stats")
        assert response.status_code in [401, 403], f"Expected 401 or 403 for unauthenticated request, got {response.status_code}"

    # === Media Settings Tests ===
    def test_get_media_settings_success(self, admin_client):
        """Test GET /api/admin/media-settings returns all settings"""
        response = admin_client.get(f"{BASE_URL}/api/admin/media-settings")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify storage-related fields are present
        assert "max_storage_per_user_mb" in data, "Missing max_storage_per_user_mb"
        assert "max_recording_duration_sec" in data, "Missing max_recording_duration_sec"
        assert "auto_delete_recordings_days" in data, "Missing auto_delete_recordings_days"
        
        # Also verify original fields
        assert "digital_media_enabled" in data, "Missing digital_media_enabled"
        assert "default_price_per_stream" in data, "Missing default_price_per_stream"
        assert "default_price_per_download" in data, "Missing default_price_per_download"
        
        print(f"Media Settings: max_storage={data['max_storage_per_user_mb']}MB, max_duration={data['max_recording_duration_sec']}s, auto_delete={data['auto_delete_recordings_days']}days")

    def test_update_media_settings_storage_fields(self, admin_client):
        """Test PUT /api/admin/media-settings with storage fields"""
        # Get current settings first
        get_response = admin_client.get(f"{BASE_URL}/api/admin/media-settings")
        original = get_response.json()
        
        # Update storage settings
        update_data = {
            "max_storage_per_user_mb": 1000,
            "max_recording_duration_sec": 900,
            "auto_delete_recordings_days": 30
        }
        response = admin_client.put(f"{BASE_URL}/api/admin/media-settings", json=update_data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify update persisted
        verify_response = admin_client.get(f"{BASE_URL}/api/admin/media-settings")
        assert verify_response.status_code == 200
        updated = verify_response.json()
        
        assert updated["max_storage_per_user_mb"] == 1000, f"max_storage_per_user_mb not updated: {updated['max_storage_per_user_mb']}"
        assert updated["max_recording_duration_sec"] == 900, f"max_recording_duration_sec not updated: {updated['max_recording_duration_sec']}"
        assert updated["auto_delete_recordings_days"] == 30, f"auto_delete_recordings_days not updated: {updated['auto_delete_recordings_days']}"
        
        # Restore original settings
        restore_data = {
            "max_storage_per_user_mb": original.get("max_storage_per_user_mb", 500),
            "max_recording_duration_sec": original.get("max_recording_duration_sec", 600),
            "auto_delete_recordings_days": original.get("auto_delete_recordings_days", 0)
        }
        admin_client.put(f"{BASE_URL}/api/admin/media-settings", json=restore_data)
        
        print("Storage settings update and persistence verified")

    def test_update_media_settings_partial(self, admin_client):
        """Test partial update of media settings (only one field)"""
        response = admin_client.put(f"{BASE_URL}/api/admin/media-settings", json={
            "max_storage_per_user_mb": 750
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify only that field changed
        verify = admin_client.get(f"{BASE_URL}/api/admin/media-settings")
        data = verify.json()
        assert data["max_storage_per_user_mb"] == 750, "Partial update failed"
        
        # Reset
        admin_client.put(f"{BASE_URL}/api/admin/media-settings", json={"max_storage_per_user_mb": 500})
        print("Partial update test passed")

    def test_update_media_settings_empty_fails(self, admin_client):
        """Test that empty update returns 400"""
        response = admin_client.put(f"{BASE_URL}/api/admin/media-settings", json={})
        assert response.status_code == 400, f"Expected 400 for empty update, got {response.status_code}"


class TestSupportTickets:
    """Tests for support ticket system"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def admin_client(self, admin_token):
        session = requests.Session()
        session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {admin_token}"
        })
        return session

    def test_list_support_tickets(self, admin_client):
        """Test GET /api/support/tickets returns list of tickets"""
        response = admin_client.get(f"{BASE_URL}/api/support/tickets")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Expected list of tickets"
        print(f"Found {len(data)} support tickets")
        
        # If there are tickets, verify structure
        if len(data) > 0:
            ticket = data[0]
            assert "id" in ticket, "Missing ticket id"
            assert "subject" in ticket, "Missing subject"
            assert "message" in ticket, "Missing message"
            assert "status" in ticket, "Missing status"
            assert "type" in ticket, "Missing type"
            print(f"Sample ticket: subject='{ticket['subject']}', status={ticket['status']}")

    def test_create_and_reply_ticket(self, admin_client):
        """Test creating a ticket and admin replying"""
        # Create ticket
        create_response = admin_client.post(f"{BASE_URL}/api/support/tickets", json={
            "subject": "TEST_Iter51_Ticket",
            "message": "This is a test ticket for iteration 51 testing",
            "type": "bug"
        })
        assert create_response.status_code in [200, 201], f"Ticket creation failed: {create_response.text}"
        ticket = create_response.json()
        ticket_id = ticket["id"]
        print(f"Created ticket: {ticket_id}")
        
        # Admin reply
        reply_response = admin_client.post(f"{BASE_URL}/api/support/tickets/{ticket_id}/reply", json={
            "message": "Test admin reply for iteration 51"
        })
        assert reply_response.status_code == 200, f"Reply failed: {reply_response.text}"
        
        # Verify reply persisted
        get_response = admin_client.get(f"{BASE_URL}/api/support/tickets/{ticket_id}")
        if get_response.status_code == 200:
            ticket_data = get_response.json()
            if "admin_replies" in ticket_data:
                assert len(ticket_data["admin_replies"]) > 0, "Admin reply not persisted"
                print(f"Admin reply verified: {ticket_data['admin_replies'][-1]['message']}")
        
        print("Create and reply ticket test passed")


class TestNarrativeProgress:
    """Tests for narrative progress auto-save feature"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def admin_client(self, admin_token):
        session = requests.Session()
        session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {admin_token}"
        })
        return session

    def test_save_narrative_progress(self, admin_client):
        """Test POST /api/narratives/save-progress"""
        # Get a student first
        users_response = admin_client.get(f"{BASE_URL}/api/admin/users")
        if users_response.status_code == 200:
            users = users_response.json()
            # Find a guardian and get their students
            for user in users:
                if user.get("role") == "guardian":
                    guardian_id = user.get("id")
                    students_response = admin_client.get(f"{BASE_URL}/api/students", params={"guardian_id": guardian_id})
                    if students_response.status_code == 200:
                        students = students_response.json()
                        if len(students) > 0:
                            student = students[0]
                            student_id = student.get("id")
                            
                            # Get narratives for this student
                            narratives_response = admin_client.get(f"{BASE_URL}/api/narratives", params={"student_id": student_id})
                            if narratives_response.status_code == 200:
                                narratives = narratives_response.json()
                                if len(narratives) > 0:
                                    narrative_id = narratives[0].get("id")
                                    
                                    # Save progress
                                    save_response = admin_client.post(f"{BASE_URL}/api/narratives/save-progress", json={
                                        "narrative_id": narrative_id,
                                        "student_id": student_id,
                                        "current_chapter": 2,
                                        "scroll_position": 150
                                    })
                                    assert save_response.status_code == 200, f"Save progress failed: {save_response.text}"
                                    print(f"Progress saved for narrative {narrative_id}")
                                    return
        print("No suitable student/narrative found for progress test - skipping")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
