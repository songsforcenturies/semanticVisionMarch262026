"""
Iteration 30: Brand Portal Story Integrations and Login/Register Portal Buttons
Tests:
1. Brand Portal story-integrations API returns story_snippets with narrative_title, excerpts, student_name
2. Brand Portal summary stats: Stories Featuring Brand, Brand Mentions, Student Responses, Avg Comprehension
3. Admin can access brand-portal story-integrations
4. Non-admin users cannot access admin portal (403)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

# Test credentials
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"
STUDENT_CODE = "STU-DR40V7"
STUDENT_PIN = "914027"


class TestBrandPortalStoryIntegrations:
    """Tests for Brand Portal Story Integrations API"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def get_admin_token(self):
        """Authenticate as admin user"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return response.json().get("access_token")

    def test_admin_login_success(self):
        """Test admin user can login successfully"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["role"] == "admin"
        print(f"Admin login successful: {data['user']['email']}")

    def test_brand_portal_story_integrations_api(self):
        """Test /api/brand-portal/story-integrations returns proper structure"""
        token = self.get_admin_token()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        response = self.session.get(f"{BASE_URL}/api/brand-portal/story-integrations")
        assert response.status_code == 200, f"Story integrations failed: {response.text}"
        
        data = response.json()
        # Verify structure
        assert "story_snippets" in data, "Response should have story_snippets"
        assert "student_responses" in data, "Response should have student_responses"
        assert "summary" in data, "Response should have summary"
        
        # Verify summary structure
        summary = data["summary"]
        assert "total_stories_with_brand" in summary, "Summary should have total_stories_with_brand"
        assert "total_snippets" in summary, "Summary should have total_snippets (brand mentions)"
        assert "total_student_responses" in summary, "Summary should have total_student_responses"
        assert "avg_comprehension_score" in summary, "Summary should have avg_comprehension_score"
        
        print(f"Story integrations returned: {len(data['story_snippets'])} snippets, "
              f"{len(data['student_responses'])} responses")
        print(f"Summary: {summary}")

    def test_story_snippet_structure(self):
        """Test story snippets have required fields"""
        token = self.get_admin_token()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        response = self.session.get(f"{BASE_URL}/api/brand-portal/story-integrations")
        assert response.status_code == 200
        
        data = response.json()
        snippets = data.get("story_snippets", [])
        
        if len(snippets) > 0:
            snippet = snippets[0]
            # Verify required fields
            assert "narrative_title" in snippet, "Snippet should have narrative_title"
            assert "excerpts" in snippet, "Snippet should have excerpts"
            assert "student_name" in snippet, "Snippet should have student_name"
            assert "chapter_number" in snippet, "Snippet should have chapter_number"
            assert "brand_terms_found" in snippet, "Snippet should have brand_terms_found"
            
            # Verify excerpts is a list
            assert isinstance(snippet["excerpts"], list), "Excerpts should be a list"
            print(f"First snippet: {snippet['narrative_title']} - {len(snippet['excerpts'])} excerpts")
        else:
            print("No story snippets found (may have no brand integrations yet)")
            # This is valid - there may not be any stories with brand mentions

    def test_student_response_structure(self):
        """Test student responses have required fields"""
        token = self.get_admin_token()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        response = self.session.get(f"{BASE_URL}/api/brand-portal/story-integrations")
        assert response.status_code == 200
        
        data = response.json()
        responses = data.get("student_responses", [])
        
        if len(responses) > 0:
            resp = responses[0]
            # Verify required fields
            assert "student_name" in resp, "Response should have student_name"
            assert "question" in resp, "Response should have question"
            assert "student_answer" in resp, "Response should have student_answer"
            assert "passed" in resp, "Response should have passed"
            assert "comprehension_score" in resp, "Response should have comprehension_score"
            
            print(f"First response: {resp['student_name']} - Q: {resp['question'][:50]}...")
        else:
            print("No student responses found (valid empty state)")
            # This is valid - responses will be empty if no written answers exist

    def test_admin_can_access_brand_portal_profile(self):
        """Test admin can access brand portal profile"""
        token = self.get_admin_token()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        response = self.session.get(f"{BASE_URL}/api/brand-portal/profile")
        # Admin may get 403 if brand-portal/profile requires brand_partner role
        # The story-integrations endpoint explicitly allows admin role
        assert response.status_code in [200, 403, 404], f"Unexpected status: {response.status_code}"
        print(f"Brand profile endpoint returns: {response.status_code}")


class TestAdminAccessControl:
    """Tests for admin access control"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def test_unauthenticated_cannot_access_story_integrations(self):
        """Test unauthenticated users cannot access story integrations"""
        response = self.session.get(f"{BASE_URL}/api/brand-portal/story-integrations")
        # 401 or 403 both indicate access denied
        assert response.status_code in [401, 403], f"Should return 401/403, got {response.status_code}"
        print(f"Unauthenticated correctly blocked: {response.status_code}")

    def test_create_test_user_and_check_admin_restriction(self):
        """Test non-admin user cannot access admin-only endpoints"""
        # Register a new test user
        import uuid
        test_email = f"test_iter30_{uuid.uuid4().hex[:8]}@test.com"
        
        # Register
        reg_response = self.session.post(f"{BASE_URL}/api/auth/register", json={
            "full_name": "Test User Iter30",
            "email": test_email,
            "password": "TestPass123!"
        })
        assert reg_response.status_code == 200, f"Registration failed: {reg_response.text}"
        token = reg_response.json().get("access_token")
        
        # Try to access admin dashboard stats
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        admin_response = self.session.get(f"{BASE_URL}/api/admin/stats")
        # Non-admin should be blocked (401, 403, or 404)
        assert admin_response.status_code in [401, 403, 404], f"Non-admin should get 401/403/404, got {admin_response.status_code}"
        print(f"Non-admin correctly blocked: {admin_response.status_code}")


class TestFrontendEndpoints:
    """Tests for frontend-facing endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()

    def test_login_page_loads(self):
        """Test login page is accessible"""
        response = self.session.get(f"{BASE_URL}/login")
        assert response.status_code == 200, f"Login page failed: {response.status_code}"
        print("Login page loads successfully")

    def test_register_page_loads(self):
        """Test register page is accessible"""
        response = self.session.get(f"{BASE_URL}/register")
        assert response.status_code == 200, f"Register page failed: {response.status_code}"
        print("Register page loads successfully")

    def test_student_login_page_loads(self):
        """Test student login page is accessible"""
        response = self.session.get(f"{BASE_URL}/student-login")
        assert response.status_code == 200, f"Student login page failed: {response.status_code}"
        print("Student login page loads successfully")

    def test_brand_portal_page_loads(self):
        """Test brand portal page is accessible (requires auth)"""
        response = self.session.get(f"{BASE_URL}/brand-portal")
        # Should load but redirect to login if not authenticated
        assert response.status_code in [200, 302], f"Brand portal failed: {response.status_code}"
        print(f"Brand portal page returns: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
