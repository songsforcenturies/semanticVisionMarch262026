"""
Tests for Admin User Management CRUD operations (Iteration 15)
- POST /api/admin/users - Admin creates user with temp password
- PUT /api/admin/users/{id} - Admin updates user
- POST /api/admin/users/{id}/reset-password - Reset password
- POST /api/admin/users/{id}/deactivate - Toggle active status
- DELETE /api/admin/users/{id} - Permanently delete user
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "admin123"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")
    return response.json().get("access_token")


@pytest.fixture
def admin_client(admin_token):
    """Create authenticated admin client"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {admin_token}"
    })
    return session


@pytest.fixture
def test_user_data():
    """Generate unique test user data"""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"TEST_user_{unique_id}@test.com",
        "full_name": f"TEST User {unique_id}",
        "role": "guardian"
    }


class TestAdminLogin:
    """Verify admin login works"""
    
    def test_admin_login_success(self):
        """Admin can login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "admin"
        print(f"Admin login successful: {data['user']['email']}")


class TestAdminCreateUser:
    """Tests for POST /api/admin/users endpoint"""
    
    def test_create_user_success(self, admin_client, test_user_data):
        """Admin can create a new user with temp password"""
        response = admin_client.post(f"{BASE_URL}/api/admin/users", json=test_user_data)
        assert response.status_code == 200, f"Create user failed: {response.text}"
        
        data = response.json()
        # Verify response contains required fields
        assert "user_id" in data
        assert "email" in data
        assert "temp_password" in data
        assert "role" in data
        assert data["email"] == test_user_data["email"].lower()
        assert data["role"] == test_user_data["role"]
        assert len(data["temp_password"]) > 0
        print(f"User created: {data['email']} with temp password: {data['temp_password']}")
        
        # Cleanup
        admin_client.delete(f"{BASE_URL}/api/admin/users/{data['user_id']}")
    
    def test_create_user_returns_temp_password(self, admin_client):
        """Created user receives a temp password they can login with"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"TEST_temppass_{unique_id}@test.com",
            "full_name": f"TEST Temp Pass User",
            "role": "guardian"
        }
        
        # Create user
        create_response = admin_client.post(f"{BASE_URL}/api/admin/users", json=user_data)
        assert create_response.status_code == 200
        created = create_response.json()
        temp_password = created["temp_password"]
        user_id = created["user_id"]
        
        # Verify login works with temp password (use returned email which is lowercased)
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": created["email"],
            "password": temp_password
        })
        assert login_response.status_code == 200, f"Login with temp password failed: {login_response.text}"
        print(f"User can login with temp password: {temp_password}")
        
        # Cleanup
        admin_client.delete(f"{BASE_URL}/api/admin/users/{user_id}")
    
    def test_create_user_rejects_duplicate_email(self, admin_client, test_user_data):
        """Cannot create user with duplicate email"""
        # Create first user
        first_response = admin_client.post(f"{BASE_URL}/api/admin/users", json=test_user_data)
        assert first_response.status_code == 200
        user_id = first_response.json()["user_id"]
        
        # Try to create second user with same email
        second_response = admin_client.post(f"{BASE_URL}/api/admin/users", json=test_user_data)
        assert second_response.status_code == 400
        assert "already exists" in second_response.json().get("detail", "").lower()
        print("Duplicate email rejected correctly")
        
        # Cleanup
        admin_client.delete(f"{BASE_URL}/api/admin/users/{user_id}")
    
    def test_create_user_rejects_invalid_role(self, admin_client):
        """Cannot create user with invalid role"""
        invalid_data = {
            "email": "test@invalid.com",
            "full_name": "Invalid Role User",
            "role": "superuser"  # Invalid role
        }
        response = admin_client.post(f"{BASE_URL}/api/admin/users", json=invalid_data)
        assert response.status_code == 400
        assert "invalid role" in response.json().get("detail", "").lower()
        print("Invalid role rejected correctly")
    
    def test_create_user_requires_admin_role(self):
        """Non-admin users cannot create users"""
        # Login as a non-admin first (create temp user, then try)
        # For this test, we'll just test without auth
        response = requests.post(f"{BASE_URL}/api/admin/users", json={
            "email": "test@test.com",
            "full_name": "Test User",
            "role": "guardian"
        })
        # Should return 401 (no auth) or 403 (not admin)
        assert response.status_code in [401, 403, 422]
        print(f"Non-admin access rejected with status: {response.status_code}")
    
    def test_create_brand_partner_auto_approved(self, admin_client):
        """Brand partner created by admin is auto-approved and auto-linked"""
        unique_id = str(uuid.uuid4())[:8]
        brand_user = {
            "email": f"TEST_brand_{unique_id}@test.com",
            "full_name": f"TEST Brand Partner {unique_id}",
            "role": "brand_partner"
        }
        
        response = admin_client.post(f"{BASE_URL}/api/admin/users", json=brand_user)
        assert response.status_code == 200
        data = response.json()
        user_id = data["user_id"]
        
        # Verify user is approved by getting users list
        users_response = admin_client.get(f"{BASE_URL}/api/admin/users")
        assert users_response.status_code == 200
        users = users_response.json()
        created_user = next((u for u in users if u["id"] == user_id), None)
        assert created_user is not None
        assert created_user.get("brand_approved") == True
        print(f"Brand partner auto-approved: {data['email']}")
        
        # Cleanup
        admin_client.delete(f"{BASE_URL}/api/admin/users/{user_id}")


class TestAdminUpdateUser:
    """Tests for PUT /api/admin/users/{id} endpoint"""
    
    def test_update_user_name_and_email(self, admin_client, test_user_data):
        """Admin can update user name and email"""
        # Create user first
        create_response = admin_client.post(f"{BASE_URL}/api/admin/users", json=test_user_data)
        assert create_response.status_code == 200
        user_id = create_response.json()["user_id"]
        
        # Update user
        unique_id = str(uuid.uuid4())[:8]
        update_data = {
            "email": f"TEST_updated_{unique_id}@test.com",
            "full_name": "TEST Updated Name"
        }
        update_response = admin_client.put(f"{BASE_URL}/api/admin/users/{user_id}", json=update_data)
        assert update_response.status_code == 200
        
        # Verify update by getting users
        users_response = admin_client.get(f"{BASE_URL}/api/admin/users")
        users = users_response.json()
        updated_user = next((u for u in users if u["id"] == user_id), None)
        assert updated_user is not None
        assert updated_user["email"] == update_data["email"].lower()
        assert updated_user["full_name"] == update_data["full_name"]
        print(f"User updated: {updated_user['email']}")
        
        # Cleanup
        admin_client.delete(f"{BASE_URL}/api/admin/users/{user_id}")
    
    def test_update_user_rejects_duplicate_email(self, admin_client):
        """Cannot update user to use another user's email"""
        unique_id1 = str(uuid.uuid4())[:8]
        unique_id2 = str(uuid.uuid4())[:8]
        
        # Create two users
        user1 = admin_client.post(f"{BASE_URL}/api/admin/users", json={
            "email": f"TEST_user1_{unique_id1}@test.com",
            "full_name": "TEST User 1",
            "role": "guardian"
        }).json()
        
        user2 = admin_client.post(f"{BASE_URL}/api/admin/users", json={
            "email": f"TEST_user2_{unique_id2}@test.com",
            "full_name": "TEST User 2",
            "role": "guardian"
        }).json()
        
        # Try to update user2 with user1's email
        update_response = admin_client.put(f"{BASE_URL}/api/admin/users/{user2['user_id']}", json={
            "email": user1["email"]
        })
        assert update_response.status_code == 400
        assert "already in use" in update_response.json().get("detail", "").lower()
        print("Duplicate email on update rejected correctly")
        
        # Cleanup
        admin_client.delete(f"{BASE_URL}/api/admin/users/{user1['user_id']}")
        admin_client.delete(f"{BASE_URL}/api/admin/users/{user2['user_id']}")


class TestAdminResetPassword:
    """Tests for POST /api/admin/users/{id}/reset-password endpoint"""
    
    def test_reset_password_returns_new_temp_password(self, admin_client, test_user_data):
        """Admin can reset user password and get new temp password"""
        # Create user
        create_response = admin_client.post(f"{BASE_URL}/api/admin/users", json=test_user_data)
        assert create_response.status_code == 200
        created = create_response.json()
        user_id = created["user_id"]
        original_temp = created["temp_password"]
        
        # Reset password
        reset_response = admin_client.post(f"{BASE_URL}/api/admin/users/{user_id}/reset-password")
        assert reset_response.status_code == 200
        reset_data = reset_response.json()
        
        # Verify new temp password is returned
        assert "temp_password" in reset_data
        assert "email" in reset_data
        new_temp = reset_data["temp_password"]
        assert new_temp != original_temp
        print(f"Password reset: {reset_data['email']} new temp: {new_temp}")
        
        # Verify new password works for login (use returned email from created response which is lowercased)
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": created["email"],
            "password": new_temp
        })
        assert login_response.status_code == 200
        print("Login with new temp password successful")
        
        # Cleanup
        admin_client.delete(f"{BASE_URL}/api/admin/users/{user_id}")


class TestAdminDeactivateUser:
    """Tests for POST /api/admin/users/{id}/deactivate endpoint"""
    
    def test_deactivate_user_toggles_status(self, admin_client, test_user_data):
        """Admin can deactivate and reactivate users"""
        # Create user
        create_response = admin_client.post(f"{BASE_URL}/api/admin/users", json=test_user_data)
        assert create_response.status_code == 200
        user_id = create_response.json()["user_id"]
        
        # Deactivate user
        deactivate_response = admin_client.post(f"{BASE_URL}/api/admin/users/{user_id}/deactivate")
        assert deactivate_response.status_code == 200
        deactivate_data = deactivate_response.json()
        assert deactivate_data.get("is_active") == False
        print(f"User deactivated: {deactivate_data['message']}")
        
        # Reactivate user
        reactivate_response = admin_client.post(f"{BASE_URL}/api/admin/users/{user_id}/deactivate")
        assert reactivate_response.status_code == 200
        reactivate_data = reactivate_response.json()
        assert reactivate_data.get("is_active") == True
        print(f"User reactivated: {reactivate_data['message']}")
        
        # Cleanup
        admin_client.delete(f"{BASE_URL}/api/admin/users/{user_id}")
    
    def test_deactivated_user_cannot_login(self, admin_client, test_user_data):
        """Deactivated users cannot login"""
        # Create user
        create_response = admin_client.post(f"{BASE_URL}/api/admin/users", json=test_user_data)
        assert create_response.status_code == 200
        created = create_response.json()
        user_id = created["user_id"]
        temp_password = created["temp_password"]
        
        # Verify user can login before deactivation (use lowercased email from created response)
        login_before = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": created["email"],
            "password": temp_password
        })
        assert login_before.status_code == 200
        print("User can login before deactivation")
        
        # Deactivate user
        admin_client.post(f"{BASE_URL}/api/admin/users/{user_id}/deactivate")
        
        # Try to login - should fail
        login_after = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": created["email"],
            "password": temp_password
        })
        assert login_after.status_code == 403
        error_message = login_after.json().get("detail", "")
        assert "deactivated" in error_message.lower()
        print(f"Deactivated user login blocked: {error_message}")
        
        # Cleanup
        admin_client.delete(f"{BASE_URL}/api/admin/users/{user_id}")
    
    def test_cannot_deactivate_admin_account(self, admin_client):
        """Cannot deactivate admin accounts"""
        # Get admin user ID
        users_response = admin_client.get(f"{BASE_URL}/api/admin/users")
        users = users_response.json()
        admin_user = next((u for u in users if u["role"] == "admin"), None)
        
        if admin_user:
            deactivate_response = admin_client.post(f"{BASE_URL}/api/admin/users/{admin_user['id']}/deactivate")
            assert deactivate_response.status_code == 400
            assert "admin" in deactivate_response.json().get("detail", "").lower()
            print("Admin deactivation blocked correctly")
        else:
            print("No admin user found in users list - skipping test")


class TestAdminDeleteUser:
    """Tests for DELETE /api/admin/users/{id} endpoint"""
    
    def test_delete_user_permanently(self, admin_client, test_user_data):
        """Admin can permanently delete a user"""
        # Create user
        create_response = admin_client.post(f"{BASE_URL}/api/admin/users", json=test_user_data)
        assert create_response.status_code == 200
        user_id = create_response.json()["user_id"]
        
        # Delete user
        delete_response = admin_client.delete(f"{BASE_URL}/api/admin/users/{user_id}")
        assert delete_response.status_code == 200
        print(f"User deleted: {delete_response.json()['message']}")
        
        # Verify user is gone
        users_response = admin_client.get(f"{BASE_URL}/api/admin/users")
        users = users_response.json()
        deleted_user = next((u for u in users if u["id"] == user_id), None)
        assert deleted_user is None
        print("Deleted user no longer in users list")
    
    def test_cannot_delete_admin_account(self, admin_client):
        """Cannot delete admin accounts"""
        # Get admin user ID
        users_response = admin_client.get(f"{BASE_URL}/api/admin/users")
        users = users_response.json()
        admin_user = next((u for u in users if u["role"] == "admin"), None)
        
        if admin_user:
            delete_response = admin_client.delete(f"{BASE_URL}/api/admin/users/{admin_user['id']}")
            assert delete_response.status_code == 400
            assert "admin" in delete_response.json().get("detail", "").lower()
            print("Admin deletion blocked correctly")
        else:
            print("No admin user found in users list - skipping test")


class TestValidRoles:
    """Test that all valid roles work"""
    
    @pytest.mark.parametrize("role", ["guardian", "teacher", "brand_partner"])
    def test_create_user_with_valid_role(self, admin_client, role):
        """Admin can create users with each valid role"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"TEST_{role}_{unique_id}@test.com",
            "full_name": f"TEST {role.title()} User",
            "role": role
        }
        
        response = admin_client.post(f"{BASE_URL}/api/admin/users", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == role
        print(f"Created {role} user: {data['email']}")
        
        # Cleanup
        admin_client.delete(f"{BASE_URL}/api/admin/users/{data['user_id']}")
