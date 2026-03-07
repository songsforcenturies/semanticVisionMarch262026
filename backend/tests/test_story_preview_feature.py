"""
Story Preview Feature Tests - Iteration 13
Tests for GET /api/brand-portal/story-preview and POST /api/brand-portal/story-preview
Features:
- Cached preview retrieval (GET)
- AI story preview generation (POST)
- Validation: returns 400 if brand has no problem_statement or products
- Authentication: requires brand_partner role
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
BRAND_PARTNER_EMAIL = "testbrand@test.com"
BRAND_PARTNER_PASSWORD = "test1234"


class TestStoryPreviewAuth:
    """Test authentication requirements for story preview endpoints"""

    def test_get_story_preview_requires_auth(self):
        """GET /api/brand-portal/story-preview should require authentication"""
        response = requests.get(f"{BASE_URL}/api/brand-portal/story-preview")
        # Server may return 401 or 403 for unauthenticated requests
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"PASSED: GET story-preview requires auth (returns {response.status_code})")

    def test_post_story_preview_requires_auth(self):
        """POST /api/brand-portal/story-preview should require authentication"""
        response = requests.post(f"{BASE_URL}/api/brand-portal/story-preview")
        # Server may return 401 or 403 for unauthenticated requests
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"PASSED: POST story-preview requires auth (returns {response.status_code})")


class TestStoryPreviewEndpoints:
    """Test story preview GET and POST endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as brand partner before each test"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": BRAND_PARTNER_EMAIL,
            "password": BRAND_PARTNER_PASSWORD
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        self.token = login_resp.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        print(f"Setup: Logged in as {BRAND_PARTNER_EMAIL}")

    def test_get_cached_preview(self):
        """GET /api/brand-portal/story-preview returns cached preview if exists"""
        response = requests.get(
            f"{BASE_URL}/api/brand-portal/story-preview",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert "preview" in data, "Response should contain 'preview' field"
        assert "generated_at" in data, "Response should contain 'generated_at' field"
        
        # Preview can be empty string if not generated yet
        assert isinstance(data["preview"], str), "Preview should be a string"
        
        # If preview exists, generated_at should be a valid timestamp
        if data["preview"]:
            assert data["generated_at"] is not None, "If preview exists, generated_at should not be None"
            print(f"PASSED: GET story-preview returns cached preview with {len(data['preview'])} chars")
        else:
            print("PASSED: GET story-preview returns empty preview (none generated yet)")

    def test_generate_story_preview(self):
        """POST /api/brand-portal/story-preview generates new AI preview"""
        # First, verify brand has problem_statement or products
        profile_resp = requests.get(
            f"{BASE_URL}/api/brand-portal/profile",
            headers=self.headers
        )
        assert profile_resp.status_code == 200
        brand = profile_resp.json().get("brand", {})
        
        has_problem = brand.get("problem_statement", "")
        has_products = len(brand.get("products", [])) > 0
        
        print(f"Brand has problem_statement: {bool(has_problem)}, has products: {has_products}")
        
        if not has_problem and not has_products:
            # Should return 400 without problem_statement or products
            response = requests.post(
                f"{BASE_URL}/api/brand-portal/story-preview",
                headers=self.headers
            )
            assert response.status_code == 400, f"Expected 400 for brand without data, got {response.status_code}"
            print("PASSED: POST returns 400 when brand has no problem_statement or products")
        else:
            # Should generate preview
            response = requests.post(
                f"{BASE_URL}/api/brand-portal/story-preview",
                headers=self.headers,
                timeout=30  # AI generation can take time
            )
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            data = response.json()
            
            # Validate response
            assert "preview" in data, "Response should contain 'preview' field"
            assert "generated_at" in data, "Response should contain 'generated_at' field"
            assert len(data["preview"]) > 50, f"Preview should be substantial, got {len(data['preview'])} chars"
            assert data["generated_at"] is not None, "generated_at should not be None"
            
            print(f"PASSED: POST story-preview generates preview with {len(data['preview'])} chars")

    def test_caching_works(self):
        """Verify GET returns same preview that was previously generated"""
        # First GET to see current state
        get1 = requests.get(
            f"{BASE_URL}/api/brand-portal/story-preview",
            headers=self.headers
        )
        assert get1.status_code == 200
        data1 = get1.json()
        
        # If we have a preview, verify it persists on subsequent GET
        if data1["preview"]:
            get2 = requests.get(
                f"{BASE_URL}/api/brand-portal/story-preview",
                headers=self.headers
            )
            assert get2.status_code == 200
            data2 = get2.json()
            
            # Should return same cached preview
            assert data1["preview"] == data2["preview"], "Cached preview should persist"
            assert data1["generated_at"] == data2["generated_at"], "Timestamp should persist"
            print("PASSED: Caching works - GET returns same preview on subsequent calls")
        else:
            print("SKIPPED: No cached preview to verify caching")


class TestStoryPreviewValidation:
    """Test validation for story preview generation"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as brand partner"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": BRAND_PARTNER_EMAIL,
            "password": BRAND_PARTNER_PASSWORD
        })
        assert login_resp.status_code == 200
        self.token = login_resp.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_preview_content_includes_brand_name(self):
        """Generated preview should mention the brand name"""
        # Get current preview
        response = requests.get(
            f"{BASE_URL}/api/brand-portal/story-preview",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Get brand name
        profile = requests.get(
            f"{BASE_URL}/api/brand-portal/profile",
            headers=self.headers
        ).json()
        brand_name = profile.get("brand", {}).get("name", "")
        
        if data["preview"] and brand_name:
            # Brand name should appear in preview (case-insensitive)
            assert brand_name.lower() in data["preview"].lower(), \
                f"Brand name '{brand_name}' should appear in preview"
            print(f"PASSED: Preview contains brand name '{brand_name}'")
        else:
            print("SKIPPED: No preview or brand name to verify content")


class TestStoryPreviewRegeneration:
    """Test regeneration of story preview"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as brand partner"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": BRAND_PARTNER_EMAIL,
            "password": BRAND_PARTNER_PASSWORD
        })
        assert login_resp.status_code == 200
        self.token = login_resp.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_regeneration_updates_preview(self):
        """POST should generate new preview overwriting cached one"""
        # Get initial state
        get1 = requests.get(
            f"{BASE_URL}/api/brand-portal/story-preview",
            headers=self.headers
        )
        assert get1.status_code == 200
        original_data = get1.json()
        original_timestamp = original_data.get("generated_at")
        
        # Check if brand can generate preview (has problem_statement or products)
        profile = requests.get(
            f"{BASE_URL}/api/brand-portal/profile",
            headers=self.headers
        ).json()
        brand = profile.get("brand", {})
        can_generate = brand.get("problem_statement") or brand.get("products", [])
        
        if not can_generate:
            print("SKIPPED: Brand has no problem_statement or products to generate preview")
            return
        
        # Generate new preview
        gen_response = requests.post(
            f"{BASE_URL}/api/brand-portal/story-preview",
            headers=self.headers,
            timeout=30
        )
        assert gen_response.status_code == 200, f"Generation failed: {gen_response.text}"
        new_data = gen_response.json()
        
        # Verify new timestamp (should be newer or different if regenerated quickly)
        assert new_data["generated_at"] is not None
        assert new_data["preview"], "New preview should not be empty"
        
        # Verify cached value is updated
        get2 = requests.get(
            f"{BASE_URL}/api/brand-portal/story-preview",
            headers=self.headers
        )
        assert get2.status_code == 200
        cached_data = get2.json()
        
        assert cached_data["preview"] == new_data["preview"], "Cache should be updated with new preview"
        assert cached_data["generated_at"] == new_data["generated_at"], "Cache timestamp should match"
        
        print("PASSED: Regeneration updates the cached preview")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
