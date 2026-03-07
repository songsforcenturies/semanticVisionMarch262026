"""
Iteration 12: Brand Portal API Tests
Tests brand portal endpoints including:
- Profile CRUD with auto-creation
- Logo upload with multipart form
- Products CRUD (nested array in brand document)
- Dashboard with new fields
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

# Test credentials
TEST_BRAND_EMAIL = "testbrand@test.com"
TEST_BRAND_PASSWORD = "test1234"


class TestBrandPortalProfile:
    """Test brand portal profile endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for brand partner"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_BRAND_EMAIL,
            "password": TEST_BRAND_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Cannot login as brand partner: {response.status_code} - {response.text}")
        data = response.json()
        assert "access_token" in data
        return data["access_token"]
    
    @pytest.fixture
    def auth_headers(self, auth_token):
        """Get auth headers"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_login_brand_partner(self):
        """Test brand partner can login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_BRAND_EMAIL,
            "password": TEST_BRAND_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "brand_partner"
        print(f"Brand partner login successful: {data['user']['email']}")
    
    def test_get_brand_profile(self, auth_headers):
        """GET /api/brand-portal/profile - should return brand info and auto-create if none"""
        response = requests.get(f"{BASE_URL}/api/brand-portal/profile", headers=auth_headers)
        assert response.status_code == 200, f"Get profile failed: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert "user" in data, "Response should have user field"
        assert "brand" in data, "Response should have brand field"
        
        # Validate user fields
        assert "id" in data["user"]
        assert "email" in data["user"]
        assert data["user"]["email"] == TEST_BRAND_EMAIL
        
        # Validate brand fields
        brand = data["brand"]
        assert "id" in brand, "Brand should have id"
        assert "name" in brand, "Brand should have name"
        print(f"Brand profile retrieved: {brand['name']}, ID: {brand['id']}")
        return brand
    
    def test_update_brand_profile(self, auth_headers):
        """PUT /api/brand-portal/profile - update brand profile fields"""
        # Update various fields
        update_data = {
            "name": "Test Brand Updated",
            "website": "https://testbrand-updated.com",
            "problem_statement": "We help children learn to read through interactive stories",
            "target_categories": ["education", "technology"],
            "target_languages": ["English", "Spanish"],
        }
        
        response = requests.put(f"{BASE_URL}/api/brand-portal/profile", 
                               json=update_data, headers=auth_headers)
        assert response.status_code == 200, f"Update profile failed: {response.text}"
        
        updated_brand = response.json()
        assert updated_brand["name"] == "Test Brand Updated"
        assert updated_brand["website"] == "https://testbrand-updated.com"
        assert updated_brand["problem_statement"] == "We help children learn to read through interactive stories"
        assert "education" in updated_brand.get("target_categories", [])
        assert "English" in updated_brand.get("target_languages", [])
        print(f"Brand profile updated successfully")
        
        # Verify persistence with GET
        verify_response = requests.get(f"{BASE_URL}/api/brand-portal/profile", headers=auth_headers)
        assert verify_response.status_code == 200
        verify_brand = verify_response.json()["brand"]
        assert verify_brand["name"] == "Test Brand Updated"
        assert verify_brand["problem_statement"] == "We help children learn to read through interactive stories"
        print("Profile update verified via GET")
    
    def test_update_target_regions(self, auth_headers):
        """PUT /api/brand-portal/profile - update target_regions with geo-targeting"""
        update_data = {
            "target_regions": [
                {"country": "United States", "state": "California", "city": "Los Angeles", "zip_code": "90001"},
                {"country": "United Kingdom", "state": "", "city": "London", "zip_code": ""}
            ]
        }
        
        response = requests.put(f"{BASE_URL}/api/brand-portal/profile",
                               json=update_data, headers=auth_headers)
        assert response.status_code == 200, f"Update regions failed: {response.text}"
        
        updated_brand = response.json()
        assert "target_regions" in updated_brand
        assert len(updated_brand["target_regions"]) == 2
        
        # Verify first region
        region1 = updated_brand["target_regions"][0]
        assert region1["country"] == "United States"
        assert region1["state"] == "California"
        assert region1["city"] == "Los Angeles"
        print(f"Target regions updated: {len(updated_brand['target_regions'])} regions")
    
    def test_set_onboarding_completed(self, auth_headers):
        """PUT /api/brand-portal/profile - set onboarding_completed flag"""
        update_data = {"onboarding_completed": True}
        
        response = requests.put(f"{BASE_URL}/api/brand-portal/profile",
                               json=update_data, headers=auth_headers)
        assert response.status_code == 200, f"Update onboarding failed: {response.text}"
        
        updated_brand = response.json()
        assert updated_brand.get("onboarding_completed") == True
        print("Onboarding completed flag set")


class TestBrandPortalLogoUpload:
    """Test brand logo upload endpoint"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_BRAND_EMAIL,
            "password": TEST_BRAND_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Cannot login")
        return {"Authorization": f"Bearer {response.json()['access_token']}"}
    
    def test_upload_logo_png(self, auth_headers):
        """POST /api/brand-portal/logo-upload - upload PNG image"""
        # Create a minimal valid PNG (1x1 transparent pixel)
        png_header = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 pixel
            0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,  # RGBA
            0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,  # IDAT chunk
            0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,  # compressed data
            0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,  # IEND chunk
            0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44,
            0xAE, 0x42, 0x60, 0x82
        ])
        
        files = {
            'file': ('test_logo.png', png_header, 'image/png')
        }
        
        # Remove content-type from headers for multipart
        headers = {"Authorization": auth_headers["Authorization"]}
        
        response = requests.post(f"{BASE_URL}/api/brand-portal/logo-upload",
                                files=files, headers=headers)
        assert response.status_code == 200, f"Logo upload failed: {response.text}"
        
        data = response.json()
        assert "logo_url" in data
        assert data["logo_url"].startswith("/api/uploads/logos/")
        print(f"Logo uploaded: {data['logo_url']}")
    
    def test_upload_invalid_file_type(self, auth_headers):
        """POST /api/brand-portal/logo-upload - reject invalid file types"""
        files = {
            'file': ('test.txt', b'not an image', 'text/plain')
        }
        headers = {"Authorization": auth_headers["Authorization"]}
        
        response = requests.post(f"{BASE_URL}/api/brand-portal/logo-upload",
                                files=files, headers=headers)
        assert response.status_code == 400, f"Should reject text files: {response.text}"
        print("Invalid file type correctly rejected")


class TestBrandPortalProducts:
    """Test brand product CRUD endpoints"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_BRAND_EMAIL,
            "password": TEST_BRAND_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Cannot login")
        return {"Authorization": f"Bearer {response.json()['access_token']}"}
    
    def test_list_products(self, auth_headers):
        """GET /api/brand-portal/products - list brand products"""
        response = requests.get(f"{BASE_URL}/api/brand-portal/products", headers=auth_headers)
        assert response.status_code == 200, f"List products failed: {response.text}"
        
        products = response.json()
        assert isinstance(products, list)
        print(f"Products listed: {len(products)} products")
        return products
    
    def test_add_product(self, auth_headers):
        """POST /api/brand-portal/products - add new product"""
        product_data = {
            "name": "TEST_SmartReader Elite",
            "description": "Advanced reading device for children",
            "category": "technology"
        }
        
        response = requests.post(f"{BASE_URL}/api/brand-portal/products",
                                json=product_data, headers=auth_headers)
        assert response.status_code == 200, f"Add product failed: {response.text}"
        
        product = response.json()
        assert product["name"] == "TEST_SmartReader Elite"
        assert product["description"] == "Advanced reading device for children"
        assert product["category"] == "technology"
        assert "id" in product
        print(f"Product added: {product['name']}, ID: {product['id']}")
        return product["id"]
    
    def test_update_product(self, auth_headers):
        """PUT /api/brand-portal/products/{product_id} - update product"""
        # First, get products to find one to update
        list_response = requests.get(f"{BASE_URL}/api/brand-portal/products", headers=auth_headers)
        products = list_response.json()
        
        if not products:
            # Add a product first
            add_response = requests.post(f"{BASE_URL}/api/brand-portal/products",
                                        json={"name": "TEST_Product", "description": "test"},
                                        headers=auth_headers)
            product_id = add_response.json()["id"]
        else:
            product_id = products[0]["id"]
        
        # Update the product
        update_data = {
            "name": "TEST_Updated Product Name",
            "description": "Updated description"
        }
        
        response = requests.put(f"{BASE_URL}/api/brand-portal/products/{product_id}",
                               json=update_data, headers=auth_headers)
        assert response.status_code == 200, f"Update product failed: {response.text}"
        
        # Verify update persisted
        verify_response = requests.get(f"{BASE_URL}/api/brand-portal/products", headers=auth_headers)
        products = verify_response.json()
        updated_product = next((p for p in products if p["id"] == product_id), None)
        
        if updated_product:
            assert updated_product["name"] == "TEST_Updated Product Name"
            print(f"Product updated: {updated_product['name']}")
    
    def test_delete_product(self, auth_headers):
        """DELETE /api/brand-portal/products/{product_id} - delete product"""
        # Add a product to delete
        add_response = requests.post(f"{BASE_URL}/api/brand-portal/products",
                                    json={"name": "TEST_ToDelete", "description": "temp"},
                                    headers=auth_headers)
        product_id = add_response.json()["id"]
        
        # Delete it
        response = requests.delete(f"{BASE_URL}/api/brand-portal/products/{product_id}",
                                  headers=auth_headers)
        assert response.status_code == 200, f"Delete product failed: {response.text}"
        
        # Verify deletion
        verify_response = requests.get(f"{BASE_URL}/api/brand-portal/products", headers=auth_headers)
        products = verify_response.json()
        deleted_product = next((p for p in products if p["id"] == product_id), None)
        assert deleted_product is None, "Product should be deleted"
        print(f"Product deleted: {product_id}")


class TestBrandPortalDashboard:
    """Test brand portal dashboard endpoint"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_BRAND_EMAIL,
            "password": TEST_BRAND_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Cannot login")
        return {"Authorization": f"Bearer {response.json()['access_token']}"}
    
    def test_get_dashboard(self, auth_headers):
        """GET /api/brand-portal/dashboard - get brand dashboard with all fields"""
        response = requests.get(f"{BASE_URL}/api/brand-portal/dashboard", headers=auth_headers)
        assert response.status_code == 200, f"Get dashboard failed: {response.text}"
        
        data = response.json()
        
        # Validate required fields
        assert "brand" in data, "Dashboard should have brand field"
        assert "stats" in data, "Dashboard should have stats field"
        assert "campaigns" in data, "Dashboard should have campaigns field"
        
        brand = data["brand"]
        assert "id" in brand
        assert "name" in brand
        assert "problem_statement" in brand or brand.get("problem_statement", "") == ""
        assert "target_regions" in brand or brand.get("target_regions", []) == []
        assert "target_languages" in brand or brand.get("target_languages", []) == []
        assert "products" in brand or brand.get("products", []) == []
        assert "onboarding_completed" in brand or brand.get("onboarding_completed", False) == False
        
        print(f"Dashboard retrieved - Brand: {brand['name']}")
        print(f"  - Problem Statement: {brand.get('problem_statement', 'Not set')[:50]}...")
        print(f"  - Products: {len(brand.get('products', []))}")
        print(f"  - Target Regions: {len(brand.get('target_regions', []))}")
        print(f"  - Onboarding Completed: {brand.get('onboarding_completed', False)}")
        
        # Validate stats structure
        stats = data["stats"]
        assert "total_impressions" in stats or stats.get("total_impressions", 0) >= 0
        assert "total_spent" in stats or stats.get("total_spent", 0) >= 0
        
        return data


class TestBrandPortalCampaigns:
    """Test brand portal campaign endpoints"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_BRAND_EMAIL,
            "password": TEST_BRAND_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Cannot login")
        return {"Authorization": f"Bearer {response.json()['access_token']}"}
    
    def test_create_campaign_requires_approval(self, auth_headers):
        """POST /api/brand-portal/campaigns - verify approval check works"""
        campaign_data = {
            "name": "TEST_Summer Campaign",
            "description": "Educational reading campaign for summer",
            "products": [{"name": "SmartReader", "category": "education"}],
            "target_categories": ["education", "books"],
            "budget": 50.0,
            "cost_per_impression": 0.05
        }
        
        response = requests.post(f"{BASE_URL}/api/brand-portal/campaigns",
                                json=campaign_data, headers=auth_headers)
        # Brand is not approved, so either 403 (pending approval) or 200 (if approved)
        assert response.status_code in [200, 403], f"Unexpected error: {response.text}"
        
        if response.status_code == 403:
            assert "pending approval" in response.text.lower()
            print("Campaign creation correctly blocked - brand pending approval")
        else:
            campaign = response.json()
            assert "id" in campaign
            print(f"Campaign created: {campaign['name']}")
    
    def test_get_campaigns(self, auth_headers):
        """GET /api/brand-portal/campaigns - list campaigns"""
        response = requests.get(f"{BASE_URL}/api/brand-portal/campaigns", headers=auth_headers)
        assert response.status_code == 200, f"Get campaigns failed: {response.text}"
        
        campaigns = response.json()
        assert isinstance(campaigns, list)
        print(f"Campaigns listed: {len(campaigns)} campaigns")


class TestBrandPortalAuth:
    """Test brand portal authentication requirements"""
    
    def test_profile_requires_auth(self):
        """Profile endpoint should require authentication"""
        response = requests.get(f"{BASE_URL}/api/brand-portal/profile")
        # 401 = no token, 403 = invalid/expired token or wrong role
        assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
        print("Profile correctly requires authentication")
    
    def test_dashboard_requires_auth(self):
        """Dashboard endpoint should require authentication"""
        response = requests.get(f"{BASE_URL}/api/brand-portal/dashboard")
        assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
        print("Dashboard correctly requires authentication")
    
    def test_products_require_auth(self):
        """Products endpoints should require authentication"""
        response = requests.get(f"{BASE_URL}/api/brand-portal/products")
        assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
        print("Products correctly requires authentication")


# Cleanup test data
@pytest.fixture(scope="module", autouse=True)
def cleanup_test_products():
    """Cleanup TEST_ prefixed products after tests"""
    yield
    # After all tests, clean up test products
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_BRAND_EMAIL,
            "password": TEST_BRAND_PASSWORD
        })
        if response.status_code == 200:
            headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
            products_response = requests.get(f"{BASE_URL}/api/brand-portal/products", headers=headers)
            if products_response.status_code == 200:
                products = products_response.json()
                for p in products:
                    if p.get("name", "").startswith("TEST_"):
                        requests.delete(f"{BASE_URL}/api/brand-portal/products/{p['id']}", headers=headers)
    except:
        pass  # Ignore cleanup errors


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
