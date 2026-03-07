"""
LexiMaster Backend API Tests
- Student Login (6-digit and 9-digit PIN support)
- Guardian Registration and Login
- Students CRUD
- Word Banks API
- Health checks
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthEndpoints:
    """Health check tests"""
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "LexiMaster API is running"
        print("✓ API root endpoint working")
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        print("✓ Health check endpoint working")


class TestStudentLogin:
    """Student login tests - CRITICAL bug fix verification"""
    
    def test_student_login_with_6_digit_pin(self):
        """Test student login with existing 6-digit PIN (Alice Johnson)"""
        response = requests.post(
            f"{BASE_URL}/api/auth/student-login",
            json={"student_code": "STU-8SXESE", "pin": "526173"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify student data returned
        assert "student" in data
        assert data["student"]["full_name"] == "Alice Johnson"
        assert data["student"]["access_pin"] == "526173"
        assert "guardian_name" in data
        print("✓ Student login with 6-digit PIN working (Alice Johnson)")
    
    def test_student_login_with_6_digit_pin_second_student(self):
        """Test student login with existing 6-digit PIN (SJ)"""
        response = requests.post(
            f"{BASE_URL}/api/auth/student-login",
            json={"student_code": "STU-DR40V7", "pin": "914027"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify student data returned
        assert "student" in data
        assert data["student"]["full_name"] == "SJ"
        assert data["student"]["access_pin"] == "914027"
        print("✓ Student login with 6-digit PIN working (SJ)")
    
    def test_student_login_wrong_pin(self):
        """Test student login with wrong PIN fails correctly"""
        response = requests.post(
            f"{BASE_URL}/api/auth/student-login",
            json={"student_code": "STU-8SXESE", "pin": "999999"}
        )
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Invalid" in data["detail"]
        print("✓ Student login with wrong PIN correctly rejected")
    
    def test_student_login_wrong_code(self):
        """Test student login with wrong student code fails"""
        response = requests.post(
            f"{BASE_URL}/api/auth/student-login",
            json={"student_code": "STU-INVALID", "pin": "526173"}
        )
        assert response.status_code == 401
        print("✓ Student login with wrong student code correctly rejected")


class TestGuardianAuth:
    """Guardian registration and login tests"""
    
    @pytest.fixture
    def test_guardian_data(self):
        """Generate unique test guardian data"""
        unique_id = str(uuid.uuid4())[:8]
        return {
            "full_name": f"TEST_Guardian_{unique_id}",
            "email": f"test_guardian_{unique_id}@example.com",
            "password": "TestPass123!",
            "role": "guardian"
        }
    
    def test_guardian_registration(self, test_guardian_data):
        """Test guardian registration"""
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=test_guardian_data
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["email"] == test_guardian_data["email"]
        assert data["full_name"] == test_guardian_data["full_name"]
        assert data["role"] == "guardian"
        print(f"✓ Guardian registration working ({test_guardian_data['email']})")
        
        # Store for subsequent tests
        return data
    
    def test_guardian_login(self, test_guardian_data):
        """Test guardian login after registration"""
        # First register
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=test_guardian_data
        )
        assert register_response.status_code == 200
        
        # Then login
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": test_guardian_data["email"],
                "password": test_guardian_data["password"]
            }
        )
        assert login_response.status_code == 200
        data = login_response.json()
        
        # Verify token returned
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == test_guardian_data["email"]
        print(f"✓ Guardian login working ({test_guardian_data['email']})")
    
    def test_guardian_login_invalid_credentials(self):
        """Test guardian login with invalid credentials fails"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "nonexistent@example.com", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        print("✓ Guardian login with invalid credentials correctly rejected")
    
    def test_duplicate_registration_fails(self, test_guardian_data):
        """Test duplicate email registration fails"""
        # First registration
        first_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=test_guardian_data
        )
        assert first_response.status_code == 200
        
        # Second registration with same email should fail
        second_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=test_guardian_data
        )
        assert second_response.status_code == 400
        assert "already registered" in second_response.json()["detail"].lower()
        print("✓ Duplicate email registration correctly rejected")


class TestWordBanks:
    """Word Bank API tests"""
    
    def test_get_word_banks(self):
        """Test fetching word banks"""
        response = requests.get(f"{BASE_URL}/api/word-banks")
        assert response.status_code == 200
        data = response.json()
        
        # Should return a list
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify word bank structure
        first_bank = data[0]
        assert "id" in first_bank
        assert "name" in first_bank
        assert "description" in first_bank
        assert "baseline_words" in first_bank
        assert "target_words" in first_bank
        assert "stretch_words" in first_bank
        print(f"✓ Word banks API working ({len(data)} banks found)")
    
    def test_get_word_bank_by_id(self):
        """Test fetching specific word bank"""
        # First get all banks
        list_response = requests.get(f"{BASE_URL}/api/word-banks")
        assert list_response.status_code == 200
        banks = list_response.json()
        
        if banks:
            bank_id = banks[0]["id"]
            # Get specific bank
            detail_response = requests.get(f"{BASE_URL}/api/word-banks/{bank_id}")
            assert detail_response.status_code == 200
            bank = detail_response.json()
            assert bank["id"] == bank_id
            print(f"✓ Word bank detail API working (bank: {bank['name']})")


class TestStudentsAPI:
    """Students CRUD API tests"""
    
    @pytest.fixture
    def authenticated_guardian(self):
        """Create and authenticate a test guardian"""
        unique_id = str(uuid.uuid4())[:8]
        guardian_data = {
            "full_name": f"TEST_Guardian_{unique_id}",
            "email": f"test_guardian_{unique_id}@example.com",
            "password": "TestPass123!",
            "role": "guardian"
        }
        
        # Register
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=guardian_data
        )
        assert register_response.status_code == 200
        user_data = register_response.json()
        
        # Login
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": guardian_data["email"], "password": guardian_data["password"]}
        )
        assert login_response.status_code == 200
        auth_data = login_response.json()
        
        return {
            "token": auth_data["access_token"],
            "user": user_data,
            "headers": {"Authorization": f"Bearer {auth_data['access_token']}"}
        }
    
    def test_create_student(self, authenticated_guardian):
        """Test creating a new student"""
        unique_id = str(uuid.uuid4())[:8]
        student_data = {
            "guardian_id": authenticated_guardian["user"]["id"],
            "full_name": f"TEST_Student_{unique_id}",
            "age": 10,
            "grade_level": "1-12",
            "interests": ["science", "art"],
            "virtues": ["curiosity"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/students",
            json=student_data,
            headers=authenticated_guardian["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify student created with PIN and code
        assert "id" in data
        assert data["full_name"] == student_data["full_name"]
        assert "access_pin" in data
        assert "student_code" in data
        
        # New students should get 9-digit PINs
        assert len(data["access_pin"]) == 9, f"Expected 9-digit PIN, got {len(data['access_pin'])}-digit"
        assert data["student_code"].startswith("STU-")
        
        print(f"✓ Student creation working (code: {data['student_code']}, PIN: {data['access_pin']})")
        return data
    
    def test_get_students_by_guardian(self, authenticated_guardian):
        """Test fetching students for a guardian"""
        guardian_id = authenticated_guardian["user"]["id"]
        
        response = requests.get(
            f"{BASE_URL}/api/students",
            params={"guardian_id": guardian_id},
            headers=authenticated_guardian["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should return a list
        assert isinstance(data, list)
        print(f"✓ Students list API working ({len(data)} students found)")
    
    def test_student_login_after_creation(self, authenticated_guardian):
        """Test that newly created student can login"""
        # Create student first
        unique_id = str(uuid.uuid4())[:8]
        student_data = {
            "guardian_id": authenticated_guardian["user"]["id"],
            "full_name": f"TEST_NewStudent_{unique_id}",
            "age": 8,
            "grade_level": "1-12",
            "interests": ["reading"],
            "virtues": ["kindness"]
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/students",
            json=student_data,
            headers=authenticated_guardian["headers"]
        )
        assert create_response.status_code == 200
        created_student = create_response.json()
        
        # Now login with the new student credentials
        login_response = requests.post(
            f"{BASE_URL}/api/auth/student-login",
            json={
                "student_code": created_student["student_code"],
                "pin": created_student["access_pin"]
            }
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        
        assert login_data["student"]["full_name"] == student_data["full_name"]
        print(f"✓ Newly created student can login (code: {created_student['student_code']})")


class TestSubscriptions:
    """Subscription API tests"""
    
    def test_get_subscription_requires_auth(self):
        """Test that subscription endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/fake-id")
        assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"
        print("✓ Subscription endpoint requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
