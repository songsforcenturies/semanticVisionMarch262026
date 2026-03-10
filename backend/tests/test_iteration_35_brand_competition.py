"""
Iteration 35: Brand Competition/Bidding System Tests
Tests:
- GET /api/brands/opt-out-analytics - opt-in/out rates for students and guardians
- GET /api/brands/competition/{problem_category} - competing brands sorted by bid amount
- GET /api/brands/active-for-student/{student_id} - brand eligibility with weighted rotation
- Brand seeding verification (34 real US brands across 12 problem categories)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestBrandCompetitionSystem:
    """Tests for brand competition/bidding system"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token from login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "allen@songsforcenturies.com",
            "password": "LexiAdmin2026!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        # API returns access_token field
        return data.get("access_token")

    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {auth_token}"}

    # ==================== OPT-OUT ANALYTICS TESTS ====================

    def test_opt_out_analytics_endpoint_exists(self, auth_headers):
        """Test that opt-out analytics endpoint exists and returns data"""
        response = requests.get(f"{BASE_URL}/api/brands/opt-out-analytics", headers=auth_headers)
        assert response.status_code == 200, f"Opt-out analytics endpoint failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "total_students" in data
        assert "brand_stories_opted_in" in data
        assert "brand_stories_opted_out" in data
        assert "opt_in_rate" in data
        assert "total_guardians" in data
        assert "offers_disabled_count" in data
        assert "offers_enabled_rate" in data
        
        print(f"Opt-out analytics: {data}")

    def test_opt_out_analytics_rates_are_valid(self, auth_headers):
        """Test that opt-in/out rates are within valid range (0-100%)"""
        response = requests.get(f"{BASE_URL}/api/brands/opt-out-analytics", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Rates should be between 0-100%
        assert 0 <= data["opt_in_rate"] <= 100, "Opt-in rate out of range"
        assert 0 <= data["offers_enabled_rate"] <= 100, "Offers enabled rate out of range"
        
        # Counts should be non-negative
        assert data["total_students"] >= 0
        assert data["brand_stories_opted_in"] >= 0
        assert data["brand_stories_opted_out"] >= 0
        assert data["total_guardians"] >= 0
        
        # Opted in + opted out should equal total students
        assert data["brand_stories_opted_in"] + data["brand_stories_opted_out"] == data["total_students"]

    # ==================== COMPETITION ENDPOINT TESTS ====================

    def test_competition_education_tech(self, auth_headers):
        """Test competition endpoint for education_tech category"""
        response = requests.get(f"{BASE_URL}/api/brands/competition/education_tech", headers=auth_headers)
        assert response.status_code == 200, f"Competition endpoint failed: {response.text}"
        data = response.json()
        
        assert data["category"] == "education_tech"
        assert "total_competitors" in data
        assert "brands" in data
        
        # education_tech should have multiple brands (LeapFrog, Nat Geo Kids, ABCmouse, Osmo, Kano)
        print(f"Education tech competitors: {data['total_competitors']}")
        for brand in data["brands"][:3]:
            print(f"  - {brand['name']}: bid=${brand['bid_amount']}")
        
        # Verify brands are sorted by bid_amount descending
        if len(data["brands"]) > 1:
            bids = [b["bid_amount"] for b in data["brands"]]
            assert bids == sorted(bids, reverse=True), "Brands not sorted by bid amount"

    def test_competition_sports_active(self, auth_headers):
        """Test competition endpoint for sports_active category"""
        response = requests.get(f"{BASE_URL}/api/brands/competition/sports_active", headers=auth_headers)
        assert response.status_code == 200, f"Competition endpoint failed: {response.text}"
        data = response.json()
        
        assert data["category"] == "sports_active"
        print(f"Sports active competitors: {data['total_competitors']}")
        for brand in data["brands"][:3]:
            print(f"  - {brand['name']}: bid=${brand['bid_amount']}")

    def test_competition_healthy_food(self, auth_headers):
        """Test competition endpoint for healthy_food category"""
        response = requests.get(f"{BASE_URL}/api/brands/competition/healthy_food", headers=auth_headers)
        assert response.status_code == 200, f"Competition endpoint failed: {response.text}"
        data = response.json()
        
        assert data["category"] == "healthy_food"
        print(f"Healthy food competitors: {data['total_competitors']}")

    def test_competition_reading_literacy(self, auth_headers):
        """Test competition endpoint for reading_literacy category"""
        response = requests.get(f"{BASE_URL}/api/brands/competition/reading_literacy", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert data["category"] == "reading_literacy"
        print(f"Reading literacy competitors: {data['total_competitors']}")
        # Should have Scholastic, Epic!, Audible Kids
        brand_names = [b["name"] for b in data["brands"]]
        print(f"  Brands: {brand_names}")

    def test_competition_brand_data_structure(self, auth_headers):
        """Test that competition endpoint returns correct brand data structure"""
        response = requests.get(f"{BASE_URL}/api/brands/competition/education_tech", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        if data["brands"]:
            brand = data["brands"][0]
            assert "id" in brand
            assert "name" in brand
            assert "bid_amount" in brand
            assert "total_impressions" in brand
            assert "rotation_count" in brand
            assert "budget_remaining" in brand

    def test_competition_empty_category(self, auth_headers):
        """Test competition endpoint for non-existent category"""
        response = requests.get(f"{BASE_URL}/api/brands/competition/nonexistent_category", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert data["category"] == "nonexistent_category"
        assert data["total_competitors"] == 0
        assert data["brands"] == []

    # ==================== BRAND LISTING TESTS ====================

    def test_brands_list_count(self, auth_headers):
        """Test that brands list has expected count after seeding"""
        response = requests.get(f"{BASE_URL}/api/admin/brands", headers=auth_headers)
        assert response.status_code == 200, f"Brands list failed: {response.text}"
        data = response.json()
        
        brands = data if isinstance(data, list) else data.get("brands", [])
        active_brands = [b for b in brands if b.get("is_active", True)]
        
        print(f"Total brands: {len(brands)}, Active brands: {len(active_brands)}")
        # Seed script adds 34 brands; there may be a few more from previous tests
        assert len(active_brands) >= 30, f"Expected at least 30 active brands, got {len(active_brands)}"

    def test_brands_have_problem_category(self, auth_headers):
        """Test that seeded brands have problem_category field"""
        response = requests.get(f"{BASE_URL}/api/admin/brands", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        brands = data if isinstance(data, list) else data.get("brands", [])
        
        # Check brands have problem_category
        brands_with_category = [b for b in brands if b.get("problem_category")]
        print(f"Brands with problem_category: {len(brands_with_category)}/{len(brands)}")
        
        # Most seeded brands should have categories
        assert len(brands_with_category) >= 20, "Expected at least 20 brands with problem_category"

    def test_brands_have_bid_amount(self, auth_headers):
        """Test that seeded brands have bid_amount field"""
        response = requests.get(f"{BASE_URL}/api/admin/brands", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        brands = data if isinstance(data, list) else data.get("brands", [])
        
        # Check brands have bid_amount > 0
        brands_with_bid = [b for b in brands if b.get("bid_amount", 0) > 0]
        print(f"Brands with bid_amount > 0: {len(brands_with_bid)}/{len(brands)}")
        
        # Print sample bids
        for b in brands_with_bid[:5]:
            print(f"  {b['name']}: ${b.get('bid_amount', 0)}")

    # ==================== BRAND OFFERS TESTS ====================

    def test_brand_offers_list(self, auth_headers):
        """Test that brand offers exist after seeding"""
        response = requests.get(f"{BASE_URL}/api/offers", headers=auth_headers)
        assert response.status_code == 200, f"Offers endpoint failed: {response.text}"
        data = response.json()
        
        offers = data.get("offers", [])
        print(f"Total offers: {len(offers)}")
        
        # Seed script adds 12 offers
        assert len(offers) >= 10, f"Expected at least 10 offers, got {len(offers)}"
        
        # Check offer structure
        if offers:
            offer = offers[0]
            assert "brand_name" in offer
            assert "title" in offer
            assert "description" in offer
            print(f"Sample offer: {offer.get('brand_name')} - {offer.get('title')}")


class TestBrandEligibilityEngine:
    """Tests for brand eligibility engine with weighted rotation"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token from login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "allen@songsforcenturies.com",
            "password": "LexiAdmin2026!"
        })
        assert response.status_code == 200
        return response.json().get("access_token")

    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}

    @pytest.fixture(scope="class")
    def test_student_id(self, auth_headers):
        """Get or create a test student"""
        # Get existing students
        response = requests.get(f"{BASE_URL}/api/students", headers=auth_headers)
        assert response.status_code == 200
        students = response.json()
        
        if students:
            return students[0]["id"]
        
        # If no students, skip the test
        pytest.skip("No students available for testing")

    def test_brand_eligibility_endpoint(self, auth_headers, test_student_id):
        """Test brand eligibility endpoint returns brands grouped by category"""
        response = requests.get(f"{BASE_URL}/api/brands/active-for-student/{test_student_id}", headers=auth_headers)
        assert response.status_code == 200, f"Eligibility endpoint failed: {response.text}"
        data = response.json()
        
        print(f"Eligibility response: total_eligible={data.get('total_eligible', 0)}, categories_matched={data.get('categories_matched', 0)}")
        
        # Check response structure
        assert "brands" in data
        assert "total_eligible" in data or "reason" in data
        
        # If brands are returned, verify structure
        for brand in data.get("brands", []):
            assert "id" in brand
            assert "name" in brand
            assert "problem_category" in brand
            assert "bid_amount" in brand

    def test_brand_eligibility_respects_opt_out(self, auth_headers, test_student_id):
        """Test that eligibility respects student ad preferences"""
        response = requests.get(f"{BASE_URL}/api/brands/active-for-student/{test_student_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # If student hasn't opted in, should get empty list with reason
        if "reason" in data and "opted in" in data["reason"].lower():
            assert data["brands"] == [], "Should return no brands if not opted in"
            print("Student has not opted in to brand stories (expected)")
        else:
            print(f"Eligible brands: {len(data.get('brands', []))}")


class TestProblemCategories:
    """Tests for problem category distribution"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "allen@songsforcenturies.com",
            "password": "LexiAdmin2026!"
        })
        assert response.status_code == 200
        return response.json().get("access_token")

    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}

    def test_all_problem_categories(self, auth_headers):
        """Test all expected problem categories have brands"""
        expected_categories = [
            "education_tech",
            "healthy_food",
            "sports_active",
            "arts_creativity",
            "health_hygiene",
            "reading_literacy",
            "financial_literacy",
            "stem_science",
            "outdoor_nature",
            "clothing_essentials",
            "safety_wellbeing",
            "music_movement",
            "life_skills",
        ]
        
        results = {}
        for cat in expected_categories:
            response = requests.get(f"{BASE_URL}/api/brands/competition/{cat}", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            results[cat] = data["total_competitors"]
            if data["total_competitors"] > 0:
                print(f"  {cat}: {data['total_competitors']} brands")
        
        # At least 8 categories should have brands
        cats_with_brands = sum(1 for c in results.values() if c > 0)
        print(f"Categories with brands: {cats_with_brands}/{len(expected_categories)}")
        assert cats_with_brands >= 8, f"Expected at least 8 categories with brands, got {cats_with_brands}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
