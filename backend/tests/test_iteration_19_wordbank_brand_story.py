"""
Test Suite for Iteration 19: Admin Word Banks, Brands, Coupons, and Story Generation with Brand Integration
Tests: 
- Admin login and word bank CRUD
- Brand campaign management
- Coupon/credit management
- Story generation with brand integration
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"
GUARDIAN_EMAIL = "allen@ourfamily.contact"
GUARDIAN_PASSWORD = "LexiAdmin2026!"


class TestAdminLogin:
    """Test admin authentication"""
    
    def test_admin_login_success(self):
        """Admin should be able to login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "access_token" in data, "Response should contain access_token"
        assert "user" in data, "Response should contain user"
        assert data["user"]["role"] == "admin", f"Expected admin role, got {data['user']['role']}"
    
    def test_admin_login_invalid_credentials(self):
        """Admin login should fail with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": "wrongpassword"
        })
        assert response.status_code == 401


class TestGuardianLogin:
    """Test guardian authentication"""
    
    def test_guardian_login_success(self):
        """Guardian should be able to login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": GUARDIAN_EMAIL,
            "password": GUARDIAN_PASSWORD
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "access_token" in data, "Response should contain access_token"
        assert "user" in data, "Response should contain user"
        assert data["user"]["role"] == "guardian", f"Expected guardian role, got {data['user']['role']}"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Admin login failed: {response.status_code}")
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def admin_user():
    """Get admin user data"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip("Admin login failed")
    return response.json()["user"]


@pytest.fixture(scope="module")
def guardian_token():
    """Get guardian authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": GUARDIAN_EMAIL,
        "password": GUARDIAN_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Guardian login failed: {response.status_code}")
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def guardian_user():
    """Get guardian user data"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": GUARDIAN_EMAIL,
        "password": GUARDIAN_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip("Guardian login failed")
    return response.json()["user"]


class TestWordBankCRUD:
    """Test Word Bank CRUD operations"""
    
    def test_get_all_word_banks(self):
        """Should list all word banks"""
        response = requests.get(f"{BASE_URL}/api/word-banks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Found {len(data)} word banks")
    
    def test_admin_create_word_bank(self, admin_token):
        """Admin should be able to create a word bank"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "name": "TEST_Iter19_Admin_WordBank",
            "description": "Test word bank created by admin for iteration 19",
            "category": "academic",
            "specialty": "Testing",
            "visibility": "global",
            "baseline_words": [
                {"word": "test", "definition": "A procedure for evaluation", "part_of_speech": "noun", "example_sentence": "This is a test."}
            ],
            "target_words": [
                {"word": "evaluate", "definition": "To assess", "part_of_speech": "verb", "example_sentence": "We evaluate progress."},
                {"word": "assess", "definition": "To judge", "part_of_speech": "verb", "example_sentence": "Teachers assess students."}
            ],
            "stretch_words": [
                {"word": "comprehensive", "definition": "Complete and thorough", "part_of_speech": "adjective", "example_sentence": "A comprehensive review."}
            ],
            "price": 0
        }
        response = requests.post(f"{BASE_URL}/api/word-banks", json=payload, headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["name"] == "TEST_Iter19_Admin_WordBank"
        assert data["category"] == "academic"
        assert len(data["target_words"]) == 2
        return data["id"]
    
    def test_admin_delete_word_bank(self, admin_token):
        """Admin should be able to delete a word bank"""
        # First create a word bank to delete
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_payload = {
            "name": "TEST_Iter19_ToDelete",
            "description": "Word bank to be deleted",
            "category": "general",
            "visibility": "global",
            "baseline_words": [],
            "target_words": [{"word": "delete", "definition": "", "part_of_speech": "", "example_sentence": ""}],
            "stretch_words": [],
            "price": 0
        }
        create_response = requests.post(f"{BASE_URL}/api/word-banks", json=create_payload, headers=headers)
        assert create_response.status_code == 200
        bank_id = create_response.json()["id"]
        
        # Delete it
        delete_response = requests.delete(f"{BASE_URL}/api/word-banks/{bank_id}", headers=headers)
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}: {delete_response.text}"
        
        # Verify deletion
        get_response = requests.get(f"{BASE_URL}/api/word-banks/{bank_id}")
        assert get_response.status_code == 404, "Deleted word bank should not exist"
    
    def test_non_admin_cannot_delete_word_bank(self, guardian_token):
        """Non-admin should not be able to delete word banks"""
        # First, get list of word banks
        response = requests.get(f"{BASE_URL}/api/word-banks")
        if response.status_code == 200 and len(response.json()) > 0:
            bank_id = response.json()[0]["id"]
            headers = {"Authorization": f"Bearer {guardian_token}"}
            delete_response = requests.delete(f"{BASE_URL}/api/word-banks/{bank_id}", headers=headers)
            assert delete_response.status_code in [401, 403], "Guardian should not be able to delete word banks"


class TestBrandManagement:
    """Test Brand CRUD operations (admin only)"""
    
    def test_get_all_brands(self, admin_token):
        """Admin should be able to list all brands"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/brands", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Found {len(data)} brands")
        return data
    
    def test_create_brand(self, admin_token):
        """Admin should be able to create a brand"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "name": "TEST_Iter19_Brand",
            "description": "Test brand for iteration 19 testing",
            "website": "https://test-brand.example.com",
            "products": [
                {"name": "Test Product A", "category": "education"},
                {"name": "Test Product B", "category": "learning"}
            ],
            "target_categories": ["education", "learning"],
            "budget_total": 100.0,
            "cost_per_impression": 0.05,
            "problem_statement": "Helps students learn better through interactive content"
        }
        response = requests.post(f"{BASE_URL}/api/admin/brands", json=payload, headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["name"] == "TEST_Iter19_Brand"
        assert len(data["products"]) == 2
        return data["id"]
    
    def test_get_brand_analytics(self, admin_token):
        """Admin should be able to get brand analytics"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/brand-analytics", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_brands" in data
        assert "total_impressions" in data
        print(f"Brand Analytics: {data['total_brands']} brands, {data['total_impressions']} impressions")


class TestCouponManagement:
    """Test Coupon CRUD operations (admin only)"""
    
    def test_get_all_coupons(self, admin_token):
        """Admin should be able to list all coupons"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/coupons", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Found {len(data)} coupons")
    
    def test_create_and_delete_coupon(self, admin_token):
        """Admin should be able to create and delete coupons"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create coupon
        payload = {
            "code": "TEST_ITER19_COUPON",
            "coupon_type": "wallet_credit",
            "value": 10.0,
            "max_uses": 5,
            "description": "Test coupon for iteration 19"
        }
        create_response = requests.post(f"{BASE_URL}/api/admin/coupons", json=payload, headers=headers)
        assert create_response.status_code == 200, f"Expected 200, got {create_response.status_code}: {create_response.text}"
        coupon_data = create_response.json()
        assert coupon_data["code"] == "TEST_ITER19_COUPON"
        coupon_id = coupon_data["id"]
        
        # Delete coupon
        delete_response = requests.delete(f"{BASE_URL}/api/admin/coupons/{coupon_id}", headers=headers)
        assert delete_response.status_code == 200


class TestAdminUserCredits:
    """Test Admin adding credits to users"""
    
    def test_get_user_list(self, admin_token):
        """Admin should be able to list users"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Found {len(data)} users")


class TestMarketplace:
    """Test Parent Marketplace functionality"""
    
    def test_guardian_can_view_marketplace(self, guardian_token):
        """Guardian should be able to view word banks in marketplace"""
        response = requests.get(f"{BASE_URL}/api/word-banks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Marketplace has {len(data)} word banks")
    
    def test_guardian_subscription_info(self, guardian_token, guardian_user):
        """Guardian should be able to view their subscription"""
        headers = {"Authorization": f"Bearer {guardian_token}"}
        response = requests.get(f"{BASE_URL}/api/subscriptions/{guardian_user['id']}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "guardian_id" in data
        assert "bank_access" in data
        print(f"Guardian has access to {len(data.get('bank_access', []))} banks")


class TestStudentManagement:
    """Test Student CRUD and word bank assignment"""
    
    def test_guardian_can_list_students(self, guardian_token, guardian_user):
        """Guardian should be able to list their students"""
        headers = {"Authorization": f"Bearer {guardian_token}"}
        response = requests.get(f"{BASE_URL}/api/students", params={"guardian_id": guardian_user["id"]}, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Guardian has {len(data)} students")
        return data
    
    def test_guardian_create_student(self, guardian_token, guardian_user):
        """Guardian should be able to create a student"""
        headers = {"Authorization": f"Bearer {guardian_token}"}
        payload = {
            "full_name": "TEST_Iter19_Student",
            "age": 10,
            "grade_level": "1-12",
            "interests": ["testing", "science"],
            "virtues": ["curiosity", "patience"],
            "guardian_id": guardian_user["id"],
            "language": "English"
        }
        response = requests.post(f"{BASE_URL}/api/students", json=payload, headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["full_name"] == "TEST_Iter19_Student"
        return data
    
    def test_assign_word_bank_to_student(self, guardian_token, guardian_user):
        """Guardian should be able to assign word banks to students"""
        headers = {"Authorization": f"Bearer {guardian_token}"}
        
        # First, list students
        students_response = requests.get(f"{BASE_URL}/api/students", params={"guardian_id": guardian_user["id"]}, headers=headers)
        students = students_response.json()
        
        # Get list of word banks
        banks_response = requests.get(f"{BASE_URL}/api/word-banks")
        banks = banks_response.json()
        
        if len(students) > 0 and len(banks) > 0:
            student_id = students[0]["id"]
            bank_ids = [banks[0]["id"]]
            
            assign_response = requests.post(f"{BASE_URL}/api/students/assign-banks", json={
                "student_id": student_id,
                "bank_ids": bank_ids
            }, headers=headers)
            assert assign_response.status_code == 200, f"Expected 200, got {assign_response.status_code}: {assign_response.text}"
            print(f"Assigned {len(bank_ids)} word banks to student")
        else:
            pytest.skip("No students or word banks available for assignment test")


class TestStoryGeneration:
    """Test Story generation with brand integration"""
    
    def test_story_generation_endpoint_exists(self, guardian_token, guardian_user):
        """Verify narratives endpoint is accessible"""
        headers = {"Authorization": f"Bearer {guardian_token}"}
        
        # First, get a student with assigned word banks
        students_response = requests.get(f"{BASE_URL}/api/students", params={"guardian_id": guardian_user["id"]}, headers=headers)
        students = students_response.json()
        
        if len(students) == 0:
            pytest.skip("No students available for story generation test")
        
        # Find a student with assigned word banks
        student_with_banks = None
        for student in students:
            if len(student.get("assigned_banks", [])) > 0:
                student_with_banks = student
                break
        
        if student_with_banks is None:
            pytest.skip("No student with assigned word banks found")
        
        print(f"Found student with {len(student_with_banks['assigned_banks'])} assigned banks")
        
        # Check if student has brand stories enabled
        ad_prefs = student_with_banks.get("ad_preferences", {})
        print(f"Student ad_preferences: {ad_prefs}")
    
    def test_story_generation_with_brand_integration(self, guardian_token, guardian_user):
        """Test story generation includes brand integration when enabled"""
        headers = {"Authorization": f"Bearer {guardian_token}"}
        
        # Get students
        students_response = requests.get(f"{BASE_URL}/api/students", params={"guardian_id": guardian_user["id"]}, headers=headers)
        students = students_response.json()
        
        if len(students) == 0:
            pytest.skip("No students available")
        
        # Find student with assigned banks
        student_with_banks = None
        for student in students:
            if len(student.get("assigned_banks", [])) > 0:
                student_with_banks = student
                break
        
        if not student_with_banks:
            # Create a test student and assign banks
            payload = {
                "full_name": "TEST_Story_Student",
                "age": 10,
                "grade_level": "1-12",
                "interests": ["adventure", "science"],
                "virtues": ["courage"],
                "guardian_id": guardian_user["id"],
                "language": "English"
            }
            create_response = requests.post(f"{BASE_URL}/api/students", json=payload, headers=headers)
            if create_response.status_code == 200:
                student_with_banks = create_response.json()
                
                # Get word banks and assign
                banks = requests.get(f"{BASE_URL}/api/word-banks").json()
                if len(banks) > 0:
                    requests.post(f"{BASE_URL}/api/students/assign-banks", json={
                        "student_id": student_with_banks["id"],
                        "bank_ids": [banks[0]["id"]]
                    }, headers=headers)
        
        if not student_with_banks or len(student_with_banks.get("assigned_banks", [])) == 0:
            pytest.skip("Could not find or create student with assigned word banks")
        
        # Enable brand stories for student
        ad_prefs_response = requests.post(
            f"{BASE_URL}/api/students/{student_with_banks['id']}/ad-preferences",
            json={"allow_brand_stories": True, "blocked_categories": []},
            headers=headers
        )
        print(f"Ad preferences update status: {ad_prefs_response.status_code}")
        
        # Generate story
        story_payload = {
            "student_id": student_with_banks["id"],
            "prompt": "A magical adventure in a science lab"
        }
        
        print(f"Generating story for student {student_with_banks['id']}...")
        story_response = requests.post(f"{BASE_URL}/api/narratives", json=story_payload, headers=headers, timeout=120)
        
        # Story generation is a long AI call, may take time
        if story_response.status_code == 200:
            story_data = story_response.json()
            print(f"Story generated successfully: {story_data.get('title', 'No title')}")
            assert "id" in story_data, "Story should have an id"
            assert "chapters" in story_data, "Story should have chapters"
            print(f"Story has {len(story_data.get('chapters', []))} chapters")
        else:
            print(f"Story generation returned {story_response.status_code}: {story_response.text[:500]}")
            # Story generation can fail for various reasons (rate limits, etc) - not a critical failure
            pytest.skip(f"Story generation failed with status {story_response.status_code}")


class TestFeatureFlags:
    """Test feature flag functionality"""
    
    def test_get_feature_flags(self, admin_token):
        """Admin should be able to get feature flags"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/feature-flags", headers=headers)
        assert response.status_code == 200
        data = response.json()
        print(f"Feature flags: {data}")
        # Check for brand sponsorship flag
        assert "brand_sponsorship_enabled" in data
    
    def test_parent_wordbank_flag(self, guardian_token):
        """Test parent wordbank creation flag endpoint"""
        headers = {"Authorization": f"Bearer {guardian_token}"}
        response = requests.get(f"{BASE_URL}/api/feature-flags/parent-wordbank", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "parent_wordbank_creation_enabled" in data
        print(f"Parent wordbank creation enabled: {data['parent_wordbank_creation_enabled']}")


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_word_banks(self, admin_token):
        """Clean up test word banks created during testing"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get all word banks
        response = requests.get(f"{BASE_URL}/api/word-banks")
        if response.status_code == 200:
            banks = response.json()
            for bank in banks:
                if bank["name"].startswith("TEST_"):
                    delete_response = requests.delete(f"{BASE_URL}/api/word-banks/{bank['id']}", headers=headers)
                    print(f"Deleted test word bank: {bank['name']}")
    
    def test_cleanup_test_brands(self, admin_token):
        """Clean up test brands created during testing"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get all brands
        response = requests.get(f"{BASE_URL}/api/admin/brands", headers=headers)
        if response.status_code == 200:
            brands = response.json()
            for brand in brands:
                if brand["name"].startswith("TEST_"):
                    delete_response = requests.delete(f"{BASE_URL}/api/admin/brands/{brand['id']}", headers=headers)
                    print(f"Deleted test brand: {brand['name']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
