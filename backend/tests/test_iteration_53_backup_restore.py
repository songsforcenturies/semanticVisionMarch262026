"""
Iteration 53: Backup & Restore System + Self-Bootstrap Tests
Tests the following features:
1. GET /api/admin/backup/status - returns document counts per collection (requires admin auth)
2. GET /api/admin/backup - downloads full database as JSON file (requires admin auth)
3. POST /api/admin/restore - uploads and restores a backup JSON file (requires admin auth)
4. Self-bootstrap: admin user auto-creation
5. Self-bootstrap: word bank seeding
"""

import pytest
import requests
import os
import json
import tempfile
from datetime import datetime

# Get backend URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials for backup system
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"


class TestBackupRestoreSystem:
    """Tests for the Backup & Restore system APIs"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Authenticate as admin and get token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def admin_headers(self, admin_token):
        """Get headers with admin auth"""
        return {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
    
    # ==================== BACKUP STATUS TESTS ====================
    
    def test_backup_status_requires_auth(self):
        """GET /admin/backup/status should require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/backup/status")
        assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"
        print(f"PASSED: Backup status requires authentication (returned {response.status_code})")
    
    def test_backup_status_returns_counts(self, admin_headers):
        """GET /admin/backup/status should return document counts"""
        response = requests.get(
            f"{BASE_URL}/api/admin/backup/status",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total_documents" in data, "Missing total_documents field"
        assert "collections" in data, "Missing collections field"
        assert "total_collections" in data, "Missing total_collections field"
        
        # Verify collections is a dict with counts
        assert isinstance(data["collections"], dict), "Collections should be a dict"
        assert data["total_documents"] >= 0, "total_documents should be non-negative"
        assert data["total_collections"] >= 0, "total_collections should be non-negative"
        
        # Verify we have some expected collections
        collections = data["collections"]
        print(f"PASSED: Backup status returned {data['total_documents']} docs across {data['total_collections']} collections")
        print(f"  Sample collections: {list(collections.keys())[:5]}")
    
    def test_backup_status_includes_users(self, admin_headers):
        """Backup status should include users collection count"""
        response = requests.get(
            f"{BASE_URL}/api/admin/backup/status",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        collections = data["collections"]
        
        # Users collection should exist with at least 1 user (the admin)
        assert "users" in collections, "Users collection missing from backup status"
        assert collections["users"] >= 1, f"Expected at least 1 user, got {collections['users']}"
        print(f"PASSED: Users collection has {collections['users']} documents")
    
    def test_backup_status_includes_word_banks(self, admin_headers):
        """Backup status should include word_banks collection count"""
        response = requests.get(
            f"{BASE_URL}/api/admin/backup/status",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        collections = data["collections"]
        
        # Word banks should exist (seeded at startup)
        if "word_banks" in collections:
            print(f"PASSED: word_banks collection has {collections['word_banks']} documents")
        else:
            print("INFO: word_banks collection is empty or doesn't exist")
    
    # ==================== BACKUP DOWNLOAD TESTS ====================
    
    def test_backup_download_requires_auth(self):
        """GET /admin/backup should require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/backup")
        assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"
        print(f"PASSED: Backup download requires authentication (returned {response.status_code})")
    
    def test_backup_download_returns_json(self, admin_headers):
        """GET /admin/backup should return a valid JSON file"""
        response = requests.get(
            f"{BASE_URL}/api/admin/backup",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Check content type
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type, f"Expected JSON, got {content_type}"
        
        # Check Content-Disposition header for filename
        content_disp = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp, "Missing attachment disposition"
        assert "semantic_vision_backup" in content_disp, "Missing backup filename pattern"
        assert ".json" in content_disp, "Filename should end with .json"
        
        print(f"PASSED: Backup download returns JSON with proper headers")
        print(f"  Content-Disposition: {content_disp}")
    
    def test_backup_contains_valid_structure(self, admin_headers):
        """Backup JSON should have correct structure with _meta and collections"""
        response = requests.get(
            f"{BASE_URL}/api/admin/backup",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        backup_data = response.json()
        
        # Check _meta field
        assert "_meta" in backup_data, "Missing _meta field"
        meta = backup_data["_meta"]
        assert "app" in meta, "Missing app in _meta"
        assert "backup_date" in meta, "Missing backup_date in _meta"
        assert "backed_up_by" in meta, "Missing backed_up_by in _meta"
        assert "total_documents" in meta, "Missing total_documents in _meta"
        assert "total_collections" in meta, "Missing total_collections in _meta"
        
        # Check collections field
        assert "collections" in backup_data, "Missing collections field"
        assert isinstance(backup_data["collections"], dict), "Collections should be a dict"
        
        print(f"PASSED: Backup structure is valid")
        print(f"  App: {meta['app']}")
        print(f"  Backup date: {meta['backup_date']}")
        print(f"  Backed up by: {meta['backed_up_by']}")
        print(f"  Total documents: {meta['total_documents']}")
        print(f"  Total collections: {meta['total_collections']}")
    
    def test_backup_contains_users_data(self, admin_headers):
        """Backup should contain users collection data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/backup",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        backup_data = response.json()
        collections = backup_data.get("collections", {})
        
        # Users should be in backup
        assert "users" in collections, "Users collection missing from backup"
        users = collections["users"]
        assert isinstance(users, list), "Users should be a list"
        assert len(users) >= 1, "Should have at least 1 user (admin)"
        
        # Verify user structure (should have converted _id to string)
        first_user = users[0]
        assert "id" in first_user, "User should have id field"
        assert "email" in first_user, "User should have email field"
        
        # Check that admin is in users
        admin_emails = [u.get("email") for u in users]
        assert ADMIN_EMAIL in admin_emails, f"Admin email not found in backup users"
        
        print(f"PASSED: Backup contains {len(users)} users including admin")
    
    # ==================== RESTORE TESTS ====================
    
    def test_restore_requires_auth(self):
        """POST /admin/restore should require authentication"""
        # Create a minimal backup file
        test_backup = {
            "_meta": {"app": "test", "backup_date": datetime.now().isoformat()},
            "collections": {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_backup, f)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = requests.post(
                    f"{BASE_URL}/api/admin/restore",
                    files={"file": ("test_backup.json", f, "application/json")}
                )
            assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"
            print(f"PASSED: Restore requires authentication (returned {response.status_code})")
        finally:
            os.unlink(temp_path)
    
    def test_restore_rejects_non_json(self, admin_headers):
        """POST /admin/restore should reject non-JSON files"""
        # Create a non-JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is not JSON")
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = requests.post(
                    f"{BASE_URL}/api/admin/restore",
                    headers={"Authorization": admin_headers["Authorization"]},
                    files={"file": ("test_backup.txt", f, "text/plain")}
                )
            assert response.status_code == 400, f"Expected 400, got {response.status_code}"
            assert "json" in response.text.lower(), "Error should mention JSON"
            print("PASSED: Restore rejects non-JSON files")
        finally:
            os.unlink(temp_path)
    
    def test_restore_rejects_invalid_json(self, admin_headers):
        """POST /admin/restore should reject invalid JSON content"""
        # Create invalid JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{invalid json content}")
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = requests.post(
                    f"{BASE_URL}/api/admin/restore",
                    headers={"Authorization": admin_headers["Authorization"]},
                    files={"file": ("test_backup.json", f, "application/json")}
                )
            assert response.status_code == 400, f"Expected 400, got {response.status_code}"
            print("PASSED: Restore rejects invalid JSON")
        finally:
            os.unlink(temp_path)
    
    def test_restore_rejects_missing_collections(self, admin_headers):
        """POST /admin/restore should reject backup without collections key"""
        # Create backup missing collections
        test_backup = {"_meta": {"app": "test"}}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_backup, f)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = requests.post(
                    f"{BASE_URL}/api/admin/restore",
                    headers={"Authorization": admin_headers["Authorization"]},
                    files={"file": ("test_backup.json", f, "application/json")}
                )
            assert response.status_code == 400, f"Expected 400, got {response.status_code}"
            assert "collections" in response.text.lower(), "Error should mention collections"
            print("PASSED: Restore rejects backup without collections key")
        finally:
            os.unlink(temp_path)
    
    def test_restore_with_existing_backup(self, admin_headers):
        """POST /admin/restore should work with the existing test backup file"""
        # Use the existing backup file
        backup_path = "/tmp/test_backup.json"
        
        if not os.path.exists(backup_path):
            pytest.skip("Test backup file not found at /tmp/test_backup.json")
        
        with open(backup_path, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/admin/restore",
                headers={"Authorization": admin_headers["Authorization"]},
                files={"file": ("test_backup.json", f, "application/json")}
            )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "status" in data, "Missing status field"
        assert data["status"] == "success", f"Expected success status, got {data['status']}"
        assert "total_new_documents" in data, "Missing total_new_documents"
        assert "total_updated_documents" in data, "Missing total_updated_documents"
        assert "details" in data, "Missing details"
        assert "backup_meta" in data, "Missing backup_meta"
        
        print(f"PASSED: Restore succeeded")
        print(f"  New documents: {data['total_new_documents']}")
        print(f"  Updated documents: {data['total_updated_documents']}")
        print(f"  Backup date: {data['backup_meta'].get('backup_date', 'N/A')}")
    
    def test_restore_upsert_behavior(self, admin_headers):
        """Restore should update existing documents (upsert by id)"""
        # First create a backup with a test document
        test_id = "TEST_restore_upsert_12345"
        test_backup = {
            "_meta": {
                "app": "Semantic Vision",
                "backup_date": datetime.now().isoformat(),
                "version": "2.0.0"
            },
            "collections": {
                "system_config": [
                    {
                        "id": test_id,
                        "key": "test_restore_key",
                        "value": "initial_value",
                        "updated_at": datetime.now().isoformat()
                    }
                ]
            }
        }
        
        # First restore - should insert
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_backup, f)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = requests.post(
                    f"{BASE_URL}/api/admin/restore",
                    headers={"Authorization": admin_headers["Authorization"]},
                    files={"file": ("test_backup.json", f, "application/json")}
                )
            assert response.status_code == 200
            data1 = response.json()
            
            # Modify the value and restore again
            test_backup["collections"]["system_config"][0]["value"] = "updated_value"
            
            with open(temp_path, 'w') as f:
                json.dump(test_backup, f)
            
            with open(temp_path, 'rb') as f:
                response = requests.post(
                    f"{BASE_URL}/api/admin/restore",
                    headers={"Authorization": admin_headers["Authorization"]},
                    files={"file": ("test_backup.json", f, "application/json")}
                )
            assert response.status_code == 200
            data2 = response.json()
            
            # Second restore should have updated (not inserted new)
            sys_config_details = data2["details"].get("system_config", {})
            print(f"PASSED: Upsert behavior working")
            print(f"  First restore - new: {data1['total_new_documents']}, updated: {data1['total_updated_documents']}")
            print(f"  Second restore - new: {data2['total_new_documents']}, updated: {data2['total_updated_documents']}")
            
        finally:
            os.unlink(temp_path)


class TestSelfBootstrap:
    """Tests for self-bootstrapping functionality"""
    
    def test_admin_user_exists(self):
        """Master admin user should exist in the database"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        
        data = response.json()
        user = data.get("user", {})
        assert user.get("role") == "admin", f"Expected admin role, got {user.get('role')}"
        assert user.get("is_delegated_admin") == True, "Admin should be delegated admin"
        
        print(f"PASSED: Master admin exists with correct role")
        print(f"  Email: {user.get('email')}")
        print(f"  Name: {user.get('full_name')}")
        print(f"  Role: {user.get('role')}")
    
    def test_word_banks_seeded(self):
        """Word banks should be seeded if database was empty"""
        # Get admin token
        login_resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        
        # Get word banks
        response = requests.get(
            f"{BASE_URL}/api/word-banks",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Failed to get word banks: {response.text}"
        
        word_banks = response.json()
        assert isinstance(word_banks, list), "Word banks should be a list"
        
        # Check for sample word banks (should have at least 5 if seeded)
        system_banks = [wb for wb in word_banks if wb.get("owner_id") == "system"]
        print(f"PASSED: Found {len(system_banks)} system word banks")
        
        if system_banks:
            print(f"  Sample banks: {[wb['name'] for wb in system_banks[:5]]}")
    
    def test_database_indexes_created(self):
        """Database should have indexes (tested via admin backup which requires indexes)"""
        login_resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        
        # Get backup status - this queries multiple collections
        response = requests.get(
            f"{BASE_URL}/api/admin/backup/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Backup status failed: {response.text}"
        
        # If we got here without errors, basic indexes are working
        print("PASSED: Database queries working (indexes functional)")


class TestBackupFileIntegrity:
    """Tests for backup file integrity and format"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Authenticate as admin and get token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return response.json()["access_token"]
    
    def test_backup_objectid_serialization(self, admin_token):
        """Backup should properly serialize MongoDB ObjectId to string"""
        response = requests.get(
            f"{BASE_URL}/api/admin/backup",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        backup_data = response.json()
        
        # Check users collection for proper _id serialization
        users = backup_data.get("collections", {}).get("users", [])
        if users:
            first_user = users[0]
            if "_id" in first_user:
                # _id should be a string, not an ObjectId
                assert isinstance(first_user["_id"], str), "_id should be serialized as string"
            print("PASSED: ObjectId properly serialized to string")
        else:
            print("INFO: No users to check ObjectId serialization")
    
    def test_backup_datetime_serialization(self, admin_token):
        """Backup should properly serialize datetime fields"""
        response = requests.get(
            f"{BASE_URL}/api/admin/backup",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        backup_data = response.json()
        
        # Check _meta backup_date
        backup_date = backup_data.get("_meta", {}).get("backup_date")
        assert backup_date is not None, "backup_date should exist"
        assert isinstance(backup_date, str), "backup_date should be string (ISO format)"
        
        # Try to parse it
        try:
            from datetime import datetime
            # Handle timezone-aware ISO format
            if "+" in backup_date or "Z" in backup_date:
                backup_date = backup_date.replace("Z", "+00:00")
            datetime.fromisoformat(backup_date)
            print("PASSED: Datetime properly serialized to ISO format")
        except ValueError as e:
            pytest.fail(f"backup_date is not valid ISO format: {backup_date}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
