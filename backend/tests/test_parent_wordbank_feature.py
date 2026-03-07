"""
Test suite for Parent Word Bank Creation feature
Tests:
1. GET /api/feature-flags/parent-wordbank - returns correct flag status
2. Admin feature flag toggle in /api/admin/feature-flags
3. POST /api/word-banks as guardian with flag enabled - should succeed
4. POST /api/word-banks as guardian with flag disabled - should return 403
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"
GUARDIAN_EMAIL = "allen@ourfamily.contact"
GUARDIAN_PASSWORD = "LexiAdmin2026!"


class TestFeatureFlagEndpoint:
    """Test the public feature flag endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def _login_guardian(self):
        """Login as guardian and return token"""
        resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": GUARDIAN_EMAIL,
            "password": GUARDIAN_PASSWORD
        })
        assert resp.status_code == 200, f"Guardian login failed: {resp.text}"
        token = resp.json().get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        return token
    
    def _login_admin(self):
        """Login as admin and return token"""
        resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200, f"Admin login failed: {resp.text}"
        token = resp.json().get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        return token
    
    def test_parent_wordbank_flag_returns_correct_format(self):
        """GET /api/feature-flags/parent-wordbank should return parent_wordbank_creation_enabled"""
        self._login_guardian()
        resp = self.session.get(f"{BASE_URL}/api/feature-flags/parent-wordbank")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "parent_wordbank_creation_enabled" in data, f"Missing key 'parent_wordbank_creation_enabled' in {data}"
        assert isinstance(data["parent_wordbank_creation_enabled"], bool), "Flag should be boolean"
        print(f"✓ Feature flag endpoint returns: {data}")


class TestAdminFeatureFlagsToggle:
    """Test admin can toggle feature flags including parent_wordbank_creation_enabled"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def _login_admin(self):
        resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200
        token = resp.json().get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        return token
    
    def test_get_feature_flags_includes_parent_wordbank(self):
        """GET /api/admin/feature-flags should include parent_wordbank_creation_enabled"""
        self._login_admin()
        resp = self.session.get(f"{BASE_URL}/api/admin/feature-flags")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "parent_wordbank_creation_enabled" in data, f"Missing parent_wordbank_creation_enabled in {data}"
        print(f"✓ Admin feature flags contains parent_wordbank_creation_enabled: {data.get('parent_wordbank_creation_enabled')}")
    
    def test_toggle_parent_wordbank_flag_on(self):
        """POST /api/admin/feature-flags can enable parent_wordbank_creation_enabled"""
        self._login_admin()
        
        # First get current flags
        resp = self.session.get(f"{BASE_URL}/api/admin/feature-flags")
        assert resp.status_code == 200
        current_flags = resp.json()
        
        # Enable the flag
        current_flags["parent_wordbank_creation_enabled"] = True
        resp = self.session.post(f"{BASE_URL}/api/admin/feature-flags", json=current_flags)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        # Verify it's enabled
        resp = self.session.get(f"{BASE_URL}/api/admin/feature-flags")
        assert resp.status_code == 200
        updated_flags = resp.json()
        assert updated_flags["parent_wordbank_creation_enabled"] == True, "Flag should be enabled"
        print("✓ Parent word bank flag successfully enabled")
    
    def test_toggle_parent_wordbank_flag_off(self):
        """POST /api/admin/feature-flags can disable parent_wordbank_creation_enabled"""
        self._login_admin()
        
        # First get current flags
        resp = self.session.get(f"{BASE_URL}/api/admin/feature-flags")
        assert resp.status_code == 200
        current_flags = resp.json()
        
        # Disable the flag
        current_flags["parent_wordbank_creation_enabled"] = False
        resp = self.session.post(f"{BASE_URL}/api/admin/feature-flags", json=current_flags)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        # Verify it's disabled
        resp = self.session.get(f"{BASE_URL}/api/admin/feature-flags")
        assert resp.status_code == 200
        updated_flags = resp.json()
        assert updated_flags["parent_wordbank_creation_enabled"] == False, "Flag should be disabled"
        print("✓ Parent word bank flag successfully disabled")


class TestGuardianWordBankCreation:
    """Test guardian word bank creation based on feature flag"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.admin_session = requests.Session()
        self.admin_session.headers.update({"Content-Type": "application/json"})
    
    def _login_guardian(self):
        resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": GUARDIAN_EMAIL,
            "password": GUARDIAN_PASSWORD
        })
        assert resp.status_code == 200
        token = resp.json().get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        return token
    
    def _login_admin(self):
        resp = self.admin_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200
        token = resp.json().get("access_token")
        self.admin_session.headers.update({"Authorization": f"Bearer {token}"})
        return token
    
    def _set_parent_wordbank_flag(self, enabled: bool):
        """Set the parent wordbank creation flag via admin API"""
        self._login_admin()
        # Get current flags
        resp = self.admin_session.get(f"{BASE_URL}/api/admin/feature-flags")
        assert resp.status_code == 200
        flags = resp.json()
        # Update flag
        flags["parent_wordbank_creation_enabled"] = enabled
        resp = self.admin_session.post(f"{BASE_URL}/api/admin/feature-flags", json=flags)
        assert resp.status_code == 200
        print(f"  → Flag set to: {enabled}")
    
    def test_guardian_create_wordbank_with_flag_enabled(self):
        """POST /api/word-banks as guardian with flag enabled should succeed"""
        # Enable the flag
        self._set_parent_wordbank_flag(True)
        
        # Login as guardian
        self._login_guardian()
        
        # Create word bank
        unique_id = str(uuid.uuid4())[:8]
        word_bank_data = {
            "name": f"TEST_Parent_WB_{unique_id}",
            "description": "Test word bank created by parent",
            "category": "general",
            "visibility": "global",
            "price": 0,
            "baseline_words": [
                {"word": "happy", "definition": "feeling joy", "part_of_speech": "adjective", "example_sentence": "I am happy."}
            ],
            "target_words": [
                {"word": "jubilant", "definition": "extremely happy", "part_of_speech": "adjective", "example_sentence": "She felt jubilant."}
            ],
            "stretch_words": []
        }
        
        resp = self.session.post(f"{BASE_URL}/api/word-banks", json=word_bank_data)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        created_bank = resp.json()
        assert "id" in created_bank, "Created word bank should have an ID"
        assert created_bank["name"] == word_bank_data["name"], "Name should match"
        print(f"✓ Guardian successfully created word bank: {created_bank.get('name')}")
    
    def test_guardian_create_wordbank_with_flag_disabled(self):
        """POST /api/word-banks as guardian with flag disabled should return 403"""
        # Disable the flag
        self._set_parent_wordbank_flag(False)
        
        # Login as guardian
        self._login_guardian()
        
        # Attempt to create word bank
        unique_id = str(uuid.uuid4())[:8]
        word_bank_data = {
            "name": f"TEST_Blocked_WB_{unique_id}",
            "description": "This should be blocked",
            "category": "general",
            "visibility": "global",
            "price": 0,
            "baseline_words": [],
            "target_words": [
                {"word": "test", "definition": "a test", "part_of_speech": "noun", "example_sentence": "This is a test."}
            ],
            "stretch_words": []
        }
        
        resp = self.session.post(f"{BASE_URL}/api/word-banks", json=word_bank_data)
        assert resp.status_code == 403, f"Expected 403 (forbidden), got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "detail" in data, "Should have error detail"
        print(f"✓ Guardian correctly blocked from creating word bank (403): {data.get('detail')}")


class TestAdminCanAlwaysCreateWordBank:
    """Test that admin can always create word banks regardless of flag"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def _login_admin(self):
        resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200
        token = resp.json().get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        return token
    
    def _set_parent_wordbank_flag(self, enabled: bool):
        """Set the parent wordbank creation flag"""
        # Get current flags
        resp = self.session.get(f"{BASE_URL}/api/admin/feature-flags")
        assert resp.status_code == 200
        flags = resp.json()
        # Update flag
        flags["parent_wordbank_creation_enabled"] = enabled
        resp = self.session.post(f"{BASE_URL}/api/admin/feature-flags", json=flags)
        assert resp.status_code == 200
    
    def test_admin_creates_wordbank_even_when_flag_disabled(self):
        """Admin can create word bank even when parent creation is disabled"""
        self._login_admin()
        
        # Disable the flag first
        self._set_parent_wordbank_flag(False)
        
        # Create word bank as admin
        unique_id = str(uuid.uuid4())[:8]
        word_bank_data = {
            "name": f"TEST_Admin_WB_{unique_id}",
            "description": "Test word bank created by admin",
            "category": "academic",
            "visibility": "global",
            "price": 0,
            "baseline_words": [],
            "target_words": [
                {"word": "eloquent", "definition": "fluent in speech", "part_of_speech": "adjective", "example_sentence": "She is eloquent."}
            ],
            "stretch_words": []
        }
        
        resp = self.session.post(f"{BASE_URL}/api/word-banks", json=word_bank_data)
        assert resp.status_code == 200, f"Admin should always be able to create word banks. Got {resp.status_code}: {resp.text}"
        
        created_bank = resp.json()
        assert "id" in created_bank
        print(f"✓ Admin successfully created word bank even with flag disabled: {created_bank.get('name')}")


@pytest.fixture(scope="session", autouse=True)
def restore_flag():
    """Ensure we restore the flag to enabled state after tests"""
    yield
    # Cleanup: re-enable the flag
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if resp.status_code == 200:
        token = resp.json().get("access_token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        resp = session.get(f"{BASE_URL}/api/admin/feature-flags")
        if resp.status_code == 200:
            flags = resp.json()
            flags["parent_wordbank_creation_enabled"] = True
            session.post(f"{BASE_URL}/api/admin/feature-flags", json=flags)
            print("\n✓ Cleanup: Restored parent_wordbank_creation_enabled to True")
