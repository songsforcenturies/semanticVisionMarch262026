"""
Iteration 10 - Brand Sponsorship System Tests
Tests for: Brand CRUD, Analytics, Classroom Sponsorships, Ad Preferences, Active-for-Student
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://vocab-hub-13.preview.emergentagent.com"

# Test credentials
ADMIN_EMAIL = "testadmin@test.com"
ADMIN_PASSWORD = "test123"
GUARDIAN_EMAIL = "newuser@test.com"
GUARDIAN_PASSWORD = "test123"


class TestBrandSponsorshipSystem:
    """Tests for brand sponsorship features - Admin brand management, analytics, sponsorships"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session and get admin token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            self.admin_token = response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
        else:
            pytest.skip(f"Admin login failed: {response.status_code}")
        
        yield
        
        # Cleanup - delete test brands
        try:
            brands = self.session.get(f"{BASE_URL}/api/admin/brands").json()
            for b in brands:
                if b["name"].startswith("TEST_"):
                    self.session.delete(f"{BASE_URL}/api/admin/brands/{b['id']}")
        except:
            pass

    # ==================== BRAND CRUD TESTS ====================

    def test_create_brand_success(self):
        """POST /api/admin/brands - create brand with products and categories"""
        brand_data = {
            "name": "TEST_LearnTech Pro",
            "description": "Educational technology products for kids",
            "website": "https://learntechpro.example.com",
            "target_categories": ["technology", "education"],
            "budget_total": 500.0,
            "cost_per_impression": 0.05,
            "products": [
                {"name": "Smart Learning Tablet", "description": "Interactive learning device", "category": "technology"},
                {"name": "Study Buddy App", "description": "AI-powered study assistant", "category": "education"}
            ]
        }
        
        response = self.session.post(f"{BASE_URL}/api/admin/brands", json=brand_data)
        
        assert response.status_code == 200 or response.status_code == 201
        data = response.json()
        
        # Validate response structure
        assert "id" in data
        assert data["name"] == "TEST_LearnTech Pro"
        assert data["description"] == "Educational technology products for kids"
        assert data["is_active"] == True
        assert data["budget_total"] == 500.0
        assert data["budget_spent"] == 0.0
        assert data["cost_per_impression"] == 0.05
        assert len(data["products"]) == 2
        assert data["products"][0]["name"] == "Smart Learning Tablet"
        assert "technology" in data["target_categories"]
        assert "education" in data["target_categories"]
        
        print(f"Created brand: {data['id']} - {data['name']}")
        return data["id"]

    def test_list_brands(self):
        """GET /api/admin/brands - list all brands"""
        response = self.session.get(f"{BASE_URL}/api/admin/brands")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"Total brands in system: {len(data)}")
        
        # Check structure if brands exist
        if len(data) > 0:
            brand = data[0]
            assert "id" in brand
            assert "name" in brand
            assert "is_active" in brand
            assert "products" in brand
            assert "budget_total" in brand
            print(f"First brand: {brand['name']} - Active: {brand['is_active']}")

    def test_update_brand_toggle_active(self):
        """PUT /api/admin/brands/{id} - update brand (toggle active/pause)"""
        # First create a brand
        create_resp = self.session.post(f"{BASE_URL}/api/admin/brands", json={
            "name": "TEST_ToggleBrand",
            "description": "Brand for toggle test",
            "budget_total": 100.0
        })
        assert create_resp.status_code in [200, 201]
        brand_id = create_resp.json()["id"]
        
        # Now toggle to inactive
        update_resp = self.session.put(f"{BASE_URL}/api/admin/brands/{brand_id}", json={
            "is_active": False
        })
        
        assert update_resp.status_code == 200
        assert update_resp.json().get("message") == "Brand updated"
        
        # Verify by fetching brands
        brands = self.session.get(f"{BASE_URL}/api/admin/brands").json()
        updated_brand = next((b for b in brands if b["id"] == brand_id), None)
        assert updated_brand is not None
        assert updated_brand["is_active"] == False
        
        # Toggle back to active
        update_resp2 = self.session.put(f"{BASE_URL}/api/admin/brands/{brand_id}", json={
            "is_active": True
        })
        assert update_resp2.status_code == 200
        
        print(f"Brand {brand_id} toggled successfully")

    def test_delete_brand(self):
        """DELETE /api/admin/brands/{id} - delete brand"""
        # Create a brand to delete
        create_resp = self.session.post(f"{BASE_URL}/api/admin/brands", json={
            "name": "TEST_DeleteBrand",
            "description": "Brand to be deleted"
        })
        assert create_resp.status_code in [200, 201]
        brand_id = create_resp.json()["id"]
        
        # Delete
        delete_resp = self.session.delete(f"{BASE_URL}/api/admin/brands/{brand_id}")
        
        assert delete_resp.status_code == 200
        assert delete_resp.json().get("message") == "Brand deleted"
        
        # Verify deleted
        brands = self.session.get(f"{BASE_URL}/api/admin/brands").json()
        deleted_brand = next((b for b in brands if b["id"] == brand_id), None)
        assert deleted_brand is None
        
        print(f"Brand {brand_id} deleted successfully")

    def test_delete_nonexistent_brand(self):
        """DELETE /api/admin/brands/{id} - returns 404 for nonexistent brand"""
        response = self.session.delete(f"{BASE_URL}/api/admin/brands/nonexistent-brand-id")
        
        assert response.status_code == 404
        assert "not found" in response.json().get("detail", "").lower()

    # ==================== BRAND ANALYTICS TESTS ====================

    def test_get_brand_analytics(self):
        """GET /api/admin/brand-analytics - brand analytics with impressions, revenue, budget"""
        response = self.session.get(f"{BASE_URL}/api/admin/brand-analytics")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate structure
        assert "total_brand_revenue" in data
        assert "total_impressions" in data
        assert "active_brands" in data
        assert "total_brands" in data
        assert "active_classroom_sponsorships" in data
        assert "total_sponsorship_amount" in data
        assert "brands" in data
        
        # Validate types
        assert isinstance(data["total_brand_revenue"], (int, float))
        assert isinstance(data["total_impressions"], int)
        assert isinstance(data["active_brands"], int)
        assert isinstance(data["total_brands"], int)
        assert isinstance(data["brands"], list)
        
        print(f"Analytics: Revenue=${data['total_brand_revenue']}, Impressions={data['total_impressions']}, Active={data['active_brands']}/{data['total_brands']}")
        
        # Check brand details if available
        if len(data["brands"]) > 0:
            brand_detail = data["brands"][0]
            assert "id" in brand_detail
            assert "name" in brand_detail
            assert "impressions" in brand_detail
            assert "budget_spent" in brand_detail
            assert "budget_remaining" in brand_detail
            print(f"First brand analytics: {brand_detail['name']} - {brand_detail['impressions']} impressions")

    # ==================== CLASSROOM SPONSORSHIP TESTS ====================

    def test_create_classroom_sponsorship(self):
        """POST /api/admin/classroom-sponsorships - create classroom sponsorship"""
        # First create a brand for sponsorship
        brand_resp = self.session.post(f"{BASE_URL}/api/admin/brands", json={
            "name": "TEST_SponsorBrand",
            "description": "Brand for sponsorship test",
            "budget_total": 1000.0
        })
        assert brand_resp.status_code in [200, 201]
        brand_id = brand_resp.json()["id"]
        
        # Create sponsorship
        sponsorship_data = {
            "brand_id": brand_id,
            "school_name": "TEST_Lincoln Elementary",
            "stories_limit": -1,  # unlimited
            "amount_paid": 500.0
        }
        
        response = self.session.post(f"{BASE_URL}/api/admin/classroom-sponsorships", json=sponsorship_data)
        
        assert response.status_code == 200 or response.status_code == 201
        data = response.json()
        
        # Validate response
        assert "id" in data
        assert data["brand_id"] == brand_id
        assert data["school_name"] == "TEST_Lincoln Elementary"
        assert data["stories_limit"] == -1
        assert data["amount_paid"] == 500.0
        assert data["is_active"] == True
        assert "badge_text" in data
        assert "Sponsored by" in data["badge_text"]
        
        print(f"Created sponsorship: {data['id']} - {data['school_name']} by {data['brand_name']}")
        return data["id"]

    def test_create_sponsorship_nonexistent_brand(self):
        """POST /api/admin/classroom-sponsorships - returns 404 for nonexistent brand"""
        sponsorship_data = {
            "brand_id": "nonexistent-brand-id",
            "school_name": "Test School",
            "stories_limit": 100,
            "amount_paid": 100.0
        }
        
        response = self.session.post(f"{BASE_URL}/api/admin/classroom-sponsorships", json=sponsorship_data)
        
        assert response.status_code == 404
        assert "brand" in response.json().get("detail", "").lower()

    def test_list_classroom_sponsorships(self):
        """GET /api/admin/classroom-sponsorships - list sponsorships"""
        response = self.session.get(f"{BASE_URL}/api/admin/classroom-sponsorships")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"Total sponsorships: {len(data)}")
        
        # Check structure if sponsorships exist
        if len(data) > 0:
            sp = data[0]
            assert "id" in sp
            assert "brand_id" in sp
            assert "brand_name" in sp
            assert "school_name" in sp
            assert "stories_limit" in sp
            assert "amount_paid" in sp
            assert "is_active" in sp
            print(f"First sponsorship: {sp['school_name']} - {sp['brand_name']}")

    def test_delete_classroom_sponsorship(self):
        """DELETE /api/admin/classroom-sponsorships/{id} - delete sponsorship"""
        # Create brand and sponsorship
        brand_resp = self.session.post(f"{BASE_URL}/api/admin/brands", json={
            "name": "TEST_DeleteSponsorBrand",
            "budget_total": 200.0
        })
        brand_id = brand_resp.json()["id"]
        
        sp_resp = self.session.post(f"{BASE_URL}/api/admin/classroom-sponsorships", json={
            "brand_id": brand_id,
            "school_name": "TEST_Delete School",
            "stories_limit": 50,
            "amount_paid": 100.0
        })
        sp_id = sp_resp.json()["id"]
        
        # Delete sponsorship
        delete_resp = self.session.delete(f"{BASE_URL}/api/admin/classroom-sponsorships/{sp_id}")
        
        assert delete_resp.status_code == 200
        assert delete_resp.json().get("message") == "Sponsorship deleted"
        
        # Verify deleted
        sponsorships = self.session.get(f"{BASE_URL}/api/admin/classroom-sponsorships").json()
        deleted_sp = next((s for s in sponsorships if s["id"] == sp_id), None)
        assert deleted_sp is None
        
        print(f"Sponsorship {sp_id} deleted successfully")


class TestStudentAdPreferences:
    """Tests for student ad preferences - Guardian opt-in/out for brand stories"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session and get guardian token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as guardian
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": GUARDIAN_EMAIL,
            "password": GUARDIAN_PASSWORD
        })
        if response.status_code == 200:
            self.guardian_token = response.json().get("access_token")
            self.user = response.json().get("user", {})
            self.session.headers.update({"Authorization": f"Bearer {self.guardian_token}"})
            print(f"Logged in as guardian: {self.user.get('full_name')}")
        else:
            pytest.skip(f"Guardian login failed: {response.status_code}")
        
        # Get students for this guardian
        students_resp = self.session.get(f"{BASE_URL}/api/students", params={"guardian_id": self.user.get("id")})
        if students_resp.status_code == 200:
            self.students = students_resp.json()
        else:
            self.students = []

    def test_get_ad_preferences_for_student(self):
        """GET /api/students/{id}/ad-preferences - get student ad preferences"""
        if not self.students:
            pytest.skip("No students for this guardian")
        
        student_id = self.students[0]["id"]
        response = self.session.get(f"{BASE_URL}/api/students/{student_id}/ad-preferences")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate structure
        assert "allow_brand_stories" in data
        assert "preferred_categories" in data
        assert "blocked_categories" in data
        
        assert isinstance(data["allow_brand_stories"], bool)
        assert isinstance(data["preferred_categories"], list)
        assert isinstance(data["blocked_categories"], list)
        
        print(f"Student {student_id} - allow_brand_stories: {data['allow_brand_stories']}")

    def test_update_ad_preferences_opt_in(self):
        """POST /api/students/{id}/ad-preferences - update student ad preferences (opt-in)"""
        if not self.students:
            pytest.skip("No students for this guardian")
        
        student_id = self.students[0]["id"]
        
        # Update to opt-in
        update_data = {
            "allow_brand_stories": True,
            "preferred_categories": ["technology", "education"],
            "blocked_categories": ["junk_food"]
        }
        
        response = self.session.post(f"{BASE_URL}/api/students/{student_id}/ad-preferences", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["allow_brand_stories"] == True
        assert "technology" in data["preferred_categories"]
        assert "junk_food" in data["blocked_categories"]
        
        print(f"Updated ad preferences for student {student_id} - opted IN")
        
        # Verify by getting again
        get_resp = self.session.get(f"{BASE_URL}/api/students/{student_id}/ad-preferences")
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        assert get_data["allow_brand_stories"] == True

    def test_update_ad_preferences_opt_out(self):
        """POST /api/students/{id}/ad-preferences - update student ad preferences (opt-out)"""
        if not self.students:
            pytest.skip("No students for this guardian")
        
        student_id = self.students[0]["id"]
        
        # Update to opt-out
        update_data = {
            "allow_brand_stories": False,
            "preferred_categories": [],
            "blocked_categories": []
        }
        
        response = self.session.post(f"{BASE_URL}/api/students/{student_id}/ad-preferences", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["allow_brand_stories"] == False
        
        print(f"Updated ad preferences for student {student_id} - opted OUT")

    def test_get_ad_preferences_nonexistent_student(self):
        """GET /api/students/{id}/ad-preferences - returns 404 for nonexistent student"""
        response = self.session.get(f"{BASE_URL}/api/students/nonexistent-student-id/ad-preferences")
        
        assert response.status_code == 404
        assert "not found" in response.json().get("detail", "").lower()


class TestActiveBrandsForStudent:
    """Tests for active-for-student endpoint - checks feature flags + guardian opt-in"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as guardian
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": GUARDIAN_EMAIL,
            "password": GUARDIAN_PASSWORD
        })
        if response.status_code == 200:
            self.guardian_token = response.json().get("access_token")
            self.user = response.json().get("user", {})
            self.session.headers.update({"Authorization": f"Bearer {self.guardian_token}"})
        else:
            pytest.skip(f"Guardian login failed: {response.status_code}")
        
        # Get students
        students_resp = self.session.get(f"{BASE_URL}/api/students", params={"guardian_id": self.user.get("id")})
        self.students = students_resp.json() if students_resp.status_code == 200 else []

    def test_active_brands_for_student_opted_out(self):
        """GET /api/brands/active-for-student/{id} - returns empty when guardian opted out"""
        if not self.students:
            pytest.skip("No students for this guardian")
        
        student_id = self.students[0]["id"]
        
        # First ensure opt-out
        self.session.post(f"{BASE_URL}/api/students/{student_id}/ad-preferences", json={
            "allow_brand_stories": False,
            "preferred_categories": [],
            "blocked_categories": []
        })
        
        response = self.session.get(f"{BASE_URL}/api/brands/active-for-student/{student_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "brands" in data
        assert data["brands"] == []
        assert "reason" in data
        assert "not opted in" in data["reason"].lower() or "has not opted in" in data["reason"].lower()
        
        print(f"Correct: No brands for opted-out student - reason: {data['reason']}")

    def test_active_brands_for_student_opted_in(self):
        """GET /api/brands/active-for-student/{id} - returns brands when guardian opted in"""
        if not self.students:
            pytest.skip("No students for this guardian")
        
        student_id = self.students[0]["id"]
        
        # Opt in
        self.session.post(f"{BASE_URL}/api/students/{student_id}/ad-preferences", json={
            "allow_brand_stories": True,
            "preferred_categories": ["technology"],
            "blocked_categories": []
        })
        
        response = self.session.get(f"{BASE_URL}/api/brands/active-for-student/{student_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "brands" in data
        assert isinstance(data["brands"], list)
        
        # May have brands or not depending on system state
        if len(data["brands"]) > 0:
            brand = data["brands"][0]
            assert "id" in brand
            assert "name" in brand
            print(f"Found {len(data['brands'])} eligible brands for student")
        else:
            print("No brands eligible (may need active brands in system)")

    def test_active_brands_nonexistent_student(self):
        """GET /api/brands/active-for-student/{id} - handles nonexistent student"""
        response = self.session.get(f"{BASE_URL}/api/brands/active-for-student/nonexistent-id")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["brands"] == []
        assert "student not found" in data["reason"].lower()


class TestFeatureFlags:
    """Tests for brand/classroom sponsorship feature flags"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with admin"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            self.admin_token = response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
        else:
            pytest.skip(f"Admin login failed: {response.status_code}")

    def test_feature_flags_include_brand_sponsorship(self):
        """GET /api/admin/feature-flags - includes brand_sponsorship_enabled"""
        response = self.session.get(f"{BASE_URL}/api/admin/feature-flags")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "brand_sponsorship_enabled" in data
        assert isinstance(data["brand_sponsorship_enabled"], bool)
        print(f"brand_sponsorship_enabled: {data['brand_sponsorship_enabled']}")

    def test_feature_flags_include_classroom_sponsorship(self):
        """GET /api/admin/feature-flags - includes classroom_sponsorship_enabled"""
        response = self.session.get(f"{BASE_URL}/api/admin/feature-flags")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "classroom_sponsorship_enabled" in data
        assert isinstance(data["classroom_sponsorship_enabled"], bool)
        print(f"classroom_sponsorship_enabled: {data['classroom_sponsorship_enabled']}")

    def test_update_brand_sponsorship_flag(self):
        """POST /api/admin/feature-flags - update brand_sponsorship_enabled"""
        # Get current value
        get_resp = self.session.get(f"{BASE_URL}/api/admin/feature-flags")
        current_value = get_resp.json().get("brand_sponsorship_enabled", True)
        
        # Toggle
        update_resp = self.session.post(f"{BASE_URL}/api/admin/feature-flags", json={
            "brand_sponsorship_enabled": not current_value
        })
        
        assert update_resp.status_code == 200
        
        # Verify toggle
        verify_resp = self.session.get(f"{BASE_URL}/api/admin/feature-flags")
        assert verify_resp.json()["brand_sponsorship_enabled"] == (not current_value)
        
        # Restore original
        self.session.post(f"{BASE_URL}/api/admin/feature-flags", json={
            "brand_sponsorship_enabled": current_value
        })
        
        print(f"Successfully toggled brand_sponsorship_enabled")


class TestAPIHealth:
    """Basic health check"""
    
    def test_api_health(self):
        """GET / - API health check"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        print(f"API healthy: {response.json()}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
