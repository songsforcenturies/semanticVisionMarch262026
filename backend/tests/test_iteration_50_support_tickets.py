"""
Iteration 50: Support Tickets & Narrative Progress Testing
Tests: Support ticket CRUD, admin reply, status updates, narrative progress save/get, brand media analytics
"""
import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://daily-screen-share.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"


class TestSupportTicketAPIs:
    """Support ticket endpoint tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, admin_token):
        """Auth headers for requests"""
        return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    
    def test_create_support_ticket(self, auth_headers):
        """POST /api/support/tickets creates a new ticket"""
        payload = {
            "subject": "TEST_Iteration50_Ticket",
            "message": "This is a test support ticket from iteration 50 testing",
            "type": "bug"
        }
        response = requests.post(f"{BASE_URL}/api/support/tickets", json=payload, headers=auth_headers)
        assert response.status_code == 200, f"Create ticket failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "id" in data, "Ticket should have id"
        assert data["subject"] == payload["subject"], "Subject should match"
        assert data["message"] == payload["message"], "Message should match"
        assert data["type"] == payload["type"], "Type should match"
        assert data["status"] == "open", "Initial status should be open"
        print(f"✓ Created support ticket: {data['id']}")
        return data["id"]
    
    def test_list_support_tickets(self, auth_headers):
        """GET /api/support/tickets lists all tickets for admin"""
        response = requests.get(f"{BASE_URL}/api/support/tickets", headers=auth_headers)
        assert response.status_code == 200, f"List tickets failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Should return a list of tickets"
        print(f"✓ Listed {len(data)} support tickets")
        
        # Check if we have the test ticket from previous iteration
        test_ticket = next((t for t in data if "Test Bug Report" in t.get("subject", "")), None)
        if test_ticket:
            print(f"  Found pre-existing test ticket with REPLIED status: {test_ticket.get('status')}")
        return data
    
    def test_admin_reply_to_ticket(self, auth_headers):
        """POST /api/support/tickets/{id}/reply admin can reply"""
        # First get list of tickets to find one to reply to
        list_response = requests.get(f"{BASE_URL}/api/support/tickets", headers=auth_headers)
        tickets = list_response.json()
        
        # Find a ticket to reply to
        ticket = next((t for t in tickets if t.get("status") != "closed"), None)
        if not ticket:
            pytest.skip("No open tickets to reply to")
        
        ticket_id = ticket["id"]
        reply_payload = {"message": "TEST_Admin reply from iteration 50 testing"}
        
        response = requests.post(f"{BASE_URL}/api/support/tickets/{ticket_id}/reply", 
                                json=reply_payload, headers=auth_headers)
        assert response.status_code == 200, f"Admin reply failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "reply" in data or "message" in data, "Should return reply confirmation"
        print(f"✓ Admin replied to ticket {ticket_id}")
    
    def test_update_ticket_status(self, auth_headers):
        """PUT /api/support/tickets/{id}/status updates status"""
        # Get list of tickets
        list_response = requests.get(f"{BASE_URL}/api/support/tickets", headers=auth_headers)
        tickets = list_response.json()
        
        # Find a ticket that's not closed
        ticket = next((t for t in tickets if t.get("status") not in ["closed", "resolved"]), None)
        if not ticket:
            pytest.skip("No open tickets to update status")
        
        ticket_id = ticket["id"]
        status_payload = {"status": "in_progress"}
        
        response = requests.put(f"{BASE_URL}/api/support/tickets/{ticket_id}/status",
                               json=status_payload, headers=auth_headers)
        assert response.status_code == 200, f"Update status failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "message" in data, "Should return status update confirmation"
        print(f"✓ Updated ticket {ticket_id} status to in_progress")
    
    def test_get_single_ticket(self, auth_headers):
        """GET /api/support/tickets/{id} gets single ticket details"""
        # Get list of tickets first
        list_response = requests.get(f"{BASE_URL}/api/support/tickets", headers=auth_headers)
        tickets = list_response.json()
        
        if not tickets:
            pytest.skip("No tickets available")
        
        ticket_id = tickets[0]["id"]
        response = requests.get(f"{BASE_URL}/api/support/tickets/{ticket_id}", headers=auth_headers)
        assert response.status_code == 200, f"Get ticket failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert data["id"] == ticket_id, "Should return the requested ticket"
        print(f"✓ Got ticket details: {data.get('subject')}")


class TestNarrativeProgressAPIs:
    """Narrative progress save/get endpoint tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.status_code}")
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, admin_token):
        return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    
    @pytest.fixture(scope="class")
    def test_narrative(self, auth_headers):
        """Get an existing narrative to test with"""
        # Get list of narratives
        response = requests.get(f"{BASE_URL}/api/narratives", headers=auth_headers)
        if response.status_code != 200:
            pytest.skip("Could not fetch narratives")
        
        narratives = response.json()
        if not narratives:
            pytest.skip("No narratives available for testing")
        
        return narratives[0]
    
    def test_save_narrative_progress(self, auth_headers, test_narrative):
        """POST /api/narratives/save-progress saves reading progress"""
        payload = {
            "narrative_id": test_narrative["id"],
            "student_id": test_narrative["student_id"],
            "current_chapter": 1,
            "scroll_position": 0.5
        }
        
        response = requests.post(f"{BASE_URL}/api/narratives/save-progress",
                                json=payload, headers=auth_headers)
        assert response.status_code == 200, f"Save progress failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "message" in data, "Should return save confirmation"
        assert data.get("current_chapter") == 1, "Should return saved chapter"
        print(f"✓ Saved narrative progress for {test_narrative['id']}")
    
    def test_get_narrative_progress(self, auth_headers, test_narrative):
        """GET /api/narratives/{id}/progress gets saved progress"""
        response = requests.get(f"{BASE_URL}/api/narratives/{test_narrative['id']}/progress",
                               headers=auth_headers)
        assert response.status_code == 200, f"Get progress failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "current_chapter" in data, "Should return current_chapter"
        assert "chapters_completed" in data, "Should return chapters_completed"
        assert "status" in data, "Should return status"
        print(f"✓ Got narrative progress: chapter {data.get('current_chapter')}, status: {data.get('status')}")


class TestBrandMediaAnalytics:
    """Brand media analytics endpoint tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.status_code}")
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, admin_token):
        return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    
    @pytest.fixture(scope="class")
    def test_brand(self, auth_headers):
        """Get an existing brand to test with"""
        response = requests.get(f"{BASE_URL}/api/admin/brands", headers=auth_headers)
        if response.status_code != 200:
            pytest.skip("Could not fetch brands")
        
        brands = response.json()
        if not brands:
            pytest.skip("No brands available for testing")
        
        return brands[0]
    
    def test_get_brand_media_analytics(self, auth_headers, test_brand):
        """GET /api/brands/{brand_id}/media-analytics returns brand media stats"""
        response = requests.get(f"{BASE_URL}/api/brands/{test_brand['id']}/media-analytics",
                               headers=auth_headers)
        assert response.status_code == 200, f"Get media analytics failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "brand_name" in data, "Should return brand_name"
        assert "total_media" in data, "Should return total_media count"
        assert "total_streams" in data, "Should return total_streams"
        assert "total_likes" in data, "Should return total_likes"
        assert "total_downloads" in data, "Should return total_downloads"
        assert "media" in data, "Should return media array"
        print(f"✓ Got brand media analytics: {data.get('total_media')} items, {data.get('total_streams')} streams")


class TestGuardianPortalMusicMediaTab:
    """Test Guardian Portal has Music & Media tab"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed")
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, admin_token):
        return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    
    def test_guardian_children_media_endpoint(self, auth_headers):
        """GET /api/guardian/children-media returns media status for all children"""
        response = requests.get(f"{BASE_URL}/api/guardian/children-media", headers=auth_headers)
        assert response.status_code == 200, f"Get children media failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Should return list of children media status"
        print(f"✓ Got children media status: {len(data)} children")
        
        # Verify structure if data exists
        if data:
            child = data[0]
            assert "student_id" in child, "Should have student_id"
            assert "student_name" in child, "Should have student_name"
            assert "digital_media_enabled" in child, "Should have digital_media_enabled flag"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
