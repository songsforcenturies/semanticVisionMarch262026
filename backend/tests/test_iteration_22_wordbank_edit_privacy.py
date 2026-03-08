"""
Iteration 22: Word Bank Edit & Privacy Testing
Testing:
- PUT /api/word-banks/{id} - admin can edit any word bank
- PUT /api/word-banks/{id} - parent can only edit their own private banks
- GET /api/word-banks?category=academic - filter by category works
- Parent creates word bank - visibility is forced to 'private'
- Parent sees global/marketplace banks + their own private banks
- Different parent does NOT see another parent's private banks
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')
if BASE_URL:
    BASE_URL = BASE_URL.rstrip('/')

# Test credentials
ADMIN_EMAIL = "allen@songsforcenturies.com"
ADMIN_PASSWORD = "LexiAdmin2026!"
GUARDIAN_EMAIL = "allen@ourfamily.contact"
GUARDIAN_PASSWORD = "LexiAdmin2026!"
OTHER_GUARDIAN_EMAIL = "other@test.com"
OTHER_GUARDIAN_PASSWORD = "Test1234!"


@pytest.fixture(scope="session")
def admin_token():
    """Get admin auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Admin login failed: {response.text}")


@pytest.fixture(scope="session")
def guardian_token():
    """Get guardian auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": GUARDIAN_EMAIL,
        "password": GUARDIAN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Guardian login failed: {response.text}")


@pytest.fixture(scope="session")
def other_guardian_token():
    """Get other guardian auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": OTHER_GUARDIAN_EMAIL,
        "password": OTHER_GUARDIAN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Other guardian login failed: {response.text}")


class TestHealthCheck:
    """Health check"""
    
    def test_backend_health(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("Backend health check PASSED")


class TestCategoryFilter:
    """Test category filtering on word banks"""
    
    def test_get_all_wordbanks_without_filter(self, admin_token):
        """Admin can get all word banks without category filter"""
        response = requests.get(f"{BASE_URL}/api/word-banks",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        banks = response.json()
        print(f"Admin sees {len(banks)} total word banks")
        # Store categories for next test
        categories = set(b.get('category') for b in banks)
        print(f"Categories present: {categories}")
    
    def test_filter_by_academic_category(self, admin_token):
        """Test filtering word banks by 'academic' category"""
        response = requests.get(f"{BASE_URL}/api/word-banks?category=academic",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        banks = response.json()
        print(f"Academic category filter returned {len(banks)} banks")
        # All returned banks should be academic
        for bank in banks:
            assert bank.get('category') == 'academic', f"Expected 'academic', got '{bank.get('category')}'"
        print("Category filter 'academic' works correctly")
    
    def test_filter_by_general_category(self, admin_token):
        """Test filtering word banks by 'general' category"""
        response = requests.get(f"{BASE_URL}/api/word-banks?category=general",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        banks = response.json()
        print(f"General category filter returned {len(banks)} banks")
        for bank in banks:
            assert bank.get('category') == 'general', f"Expected 'general', got '{bank.get('category')}'"
        print("Category filter 'general' works correctly")
    
    def test_filter_by_specialized_category(self, admin_token):
        """Test filtering word banks by 'specialized' category"""
        response = requests.get(f"{BASE_URL}/api/word-banks?category=specialized",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        banks = response.json()
        print(f"Specialized category filter returned {len(banks)} banks")
        for bank in banks:
            assert bank.get('category') == 'specialized', f"Expected 'specialized', got '{bank.get('category')}'"
        print("Category filter 'specialized' works correctly")


class TestAdminEditWordBank:
    """Test admin can edit any word bank"""
    
    def test_admin_can_edit_wordbank_name(self, admin_token):
        """Admin can edit any word bank's name"""
        # First get all word banks
        response = requests.get(f"{BASE_URL}/api/word-banks",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        banks = response.json()
        
        if len(banks) == 0:
            pytest.skip("No word banks to test edit")
        
        # Pick first bank
        bank = banks[0]
        bank_id = bank.get('id')
        original_name = bank.get('name')
        
        # Update with TEST_ prefix
        new_name = f"TEST_EDIT_{original_name}"
        response = requests.put(f"{BASE_URL}/api/word-banks/{bank_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": new_name})
        assert response.status_code == 200, f"Edit failed: {response.text}"
        updated = response.json()
        assert updated.get('name') == new_name, f"Name not updated: expected '{new_name}', got '{updated.get('name')}'"
        print(f"Admin edited word bank name from '{original_name}' to '{new_name}'")
        
        # Revert back
        response = requests.put(f"{BASE_URL}/api/word-banks/{bank_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": original_name})
        assert response.status_code == 200
        print(f"Reverted name back to '{original_name}'")
    
    def test_admin_can_edit_wordbank_description(self, admin_token):
        """Admin can edit word bank's description"""
        response = requests.get(f"{BASE_URL}/api/word-banks",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        banks = response.json()
        
        if len(banks) == 0:
            pytest.skip("No word banks to test edit")
        
        bank = banks[0]
        bank_id = bank.get('id')
        original_desc = bank.get('description')
        
        # Update description
        new_desc = "TEST_EDIT_Description for testing purposes"
        response = requests.put(f"{BASE_URL}/api/word-banks/{bank_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"description": new_desc})
        assert response.status_code == 200
        updated = response.json()
        assert updated.get('description') == new_desc
        print(f"Admin edited word bank description successfully")
        
        # Revert back
        response = requests.put(f"{BASE_URL}/api/word-banks/{bank_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"description": original_desc})
        assert response.status_code == 200
        print("Reverted description back")
    
    def test_admin_can_edit_wordbank_category(self, admin_token):
        """Admin can edit word bank's category"""
        response = requests.get(f"{BASE_URL}/api/word-banks",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        banks = response.json()
        
        if len(banks) == 0:
            pytest.skip("No word banks to test edit")
        
        bank = banks[0]
        bank_id = bank.get('id')
        original_category = bank.get('category')
        
        # Change category
        new_category = 'specialized' if original_category != 'specialized' else 'academic'
        response = requests.put(f"{BASE_URL}/api/word-banks/{bank_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"category": new_category})
        assert response.status_code == 200
        updated = response.json()
        assert updated.get('category') == new_category
        print(f"Admin changed category from '{original_category}' to '{new_category}'")
        
        # Revert
        response = requests.put(f"{BASE_URL}/api/word-banks/{bank_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"category": original_category})
        assert response.status_code == 200
        print("Reverted category back")
    
    def test_admin_can_edit_wordbank_price(self, admin_token):
        """Admin can edit word bank's price"""
        response = requests.get(f"{BASE_URL}/api/word-banks",
            headers={"Authorization": f"Bearer {admin_token}"})
        banks = response.json()
        
        if len(banks) == 0:
            pytest.skip("No word banks to test")
        
        bank = banks[0]
        bank_id = bank.get('id')
        original_price = bank.get('price', 0)
        
        # Change price
        new_price = 500  # $5.00
        response = requests.put(f"{BASE_URL}/api/word-banks/{bank_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"price": new_price})
        assert response.status_code == 200
        updated = response.json()
        assert updated.get('price') == new_price
        print(f"Admin changed price from {original_price} to {new_price}")
        
        # Revert
        response = requests.put(f"{BASE_URL}/api/word-banks/{bank_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"price": original_price})
        assert response.status_code == 200
        print("Reverted price back")
    
    def test_admin_can_edit_wordbank_words(self, admin_token):
        """Admin can edit word bank's words"""
        response = requests.get(f"{BASE_URL}/api/word-banks",
            headers={"Authorization": f"Bearer {admin_token}"})
        banks = response.json()
        
        if len(banks) == 0:
            pytest.skip("No word banks to test")
        
        bank = banks[0]
        bank_id = bank.get('id')
        original_target_words = bank.get('target_words', [])
        
        # Add a test word
        new_target_words = original_target_words + [{"word": "TEST_WORD_123", "definition": "", "part_of_speech": "", "example_sentence": ""}]
        response = requests.put(f"{BASE_URL}/api/word-banks/{bank_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"target_words": new_target_words})
        assert response.status_code == 200
        updated = response.json()
        assert len(updated.get('target_words', [])) == len(new_target_words)
        print(f"Admin added test word to target_words")
        
        # Revert
        response = requests.put(f"{BASE_URL}/api/word-banks/{bank_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"target_words": original_target_words})
        assert response.status_code == 200
        print("Reverted target_words back")


class TestParentPrivacyEnforcement:
    """Test parent-created word banks are forced to private"""
    
    def test_parent_wordbank_forced_private(self, guardian_token):
        """Parent creating word bank has visibility forced to private even if global requested"""
        # Create a word bank with visibility='global' - should be forced to private
        response = requests.post(f"{BASE_URL}/api/word-banks",
            headers={"Authorization": f"Bearer {guardian_token}"},
            json={
                "name": "TEST_PARENT_PRIVACY_CHECK",
                "description": "Testing privacy enforcement",
                "category": "general",
                "visibility": "global",  # Requesting global, should be forced to private
                "target_words": [{"word": "test", "definition": "", "part_of_speech": "", "example_sentence": ""}],
                "price": 0
            })
        assert response.status_code == 200, f"Create failed: {response.text}"
        bank = response.json()
        test_bank_id = bank.get('id')
        
        # Verify visibility was forced to private
        assert bank.get('visibility') == 'private', f"Expected 'private', got '{bank.get('visibility')}'"
        assert bank.get('created_by_role') == 'guardian', f"Expected 'guardian', got '{bank.get('created_by_role')}'"
        print("Parent-created word bank was forced to 'private' visibility")
        
        # Cleanup: Admin deletes the test bank
        admin_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        admin_token = admin_response.json().get("access_token")
        delete_response = requests.delete(f"{BASE_URL}/api/word-banks/{test_bank_id}",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert delete_response.status_code == 200
        print("Test word bank deleted successfully")


class TestParentCanEditOwnBank:
    """Test parent can only edit their own private banks"""
    
    def test_find_parent_private_bank(self, guardian_token):
        """Guardian can see their own private bank"""
        response = requests.get(f"{BASE_URL}/api/word-banks",
            headers={"Authorization": f"Bearer {guardian_token}"})
        assert response.status_code == 200
        banks = response.json()
        
        # Look for parent-created private bank
        parent_banks = [b for b in banks if b.get('created_by_role') == 'guardian' and b.get('visibility') == 'private']
        print(f"Guardian sees {len(parent_banks)} private parent-created banks")
        
        # Guardian should also see global banks
        global_banks = [b for b in banks if b.get('visibility') in ['global', 'marketplace']]
        print(f"Guardian sees {len(global_banks)} global/marketplace banks")
        
        assert len(banks) > 0, "Guardian should see at least global banks"
    
    def test_parent_can_edit_own_bank(self, guardian_token):
        """Parent can edit their own private word bank"""
        # First get guardian's banks
        response = requests.get(f"{BASE_URL}/api/word-banks",
            headers={"Authorization": f"Bearer {guardian_token}"})
        banks = response.json()
        
        # Find a parent-created bank (My Family Words)
        parent_bank = next((b for b in banks if b.get('created_by_role') == 'guardian' and b.get('visibility') == 'private'), None)
        if not parent_bank:
            pytest.skip("No parent-created private bank found for testing")
        
        bank_id = parent_bank.get('id')
        original_desc = parent_bank.get('description')
        
        # Edit description
        new_desc = "TEST_PARENT_EDIT_" + (original_desc or "description")
        response = requests.put(f"{BASE_URL}/api/word-banks/{bank_id}",
            headers={"Authorization": f"Bearer {guardian_token}"},
            json={"description": new_desc})
        assert response.status_code == 200, f"Edit failed: {response.text}"
        updated = response.json()
        assert updated.get('description') == new_desc
        print(f"Parent successfully edited their own word bank")
        
        # Revert
        response = requests.put(f"{BASE_URL}/api/word-banks/{bank_id}",
            headers={"Authorization": f"Bearer {guardian_token}"},
            json={"description": original_desc})
        assert response.status_code == 200
        print("Reverted description")
    
    def test_parent_cannot_change_visibility_from_private(self, guardian_token):
        """Parent cannot change visibility from private to global"""
        # Get parent's private bank
        response = requests.get(f"{BASE_URL}/api/word-banks",
            headers={"Authorization": f"Bearer {guardian_token}"})
        banks = response.json()
        
        parent_bank = next((b for b in banks if b.get('created_by_role') == 'guardian' and b.get('visibility') == 'private'), None)
        if not parent_bank:
            pytest.skip("No parent-created private bank found")
        
        bank_id = parent_bank.get('id')
        
        # Try to change visibility to global
        response = requests.put(f"{BASE_URL}/api/word-banks/{bank_id}",
            headers={"Authorization": f"Bearer {guardian_token}"},
            json={"visibility": "global"})
        assert response.status_code == 200  # Request succeeds but visibility stays private
        updated = response.json()
        assert updated.get('visibility') == 'private', f"Visibility should remain 'private', got '{updated.get('visibility')}'"
        print("Parent cannot change visibility from private - forced to stay private")
    
    def test_parent_cannot_edit_global_bank(self, guardian_token, admin_token):
        """Parent cannot edit a global (admin-created) word bank"""
        # Get all banks as admin to find a global admin-created bank
        response = requests.get(f"{BASE_URL}/api/word-banks",
            headers={"Authorization": f"Bearer {admin_token}"})
        banks = response.json()
        
        global_admin_bank = next((b for b in banks if b.get('created_by_role') == 'admin' and b.get('visibility') == 'global'), None)
        if not global_admin_bank:
            pytest.skip("No global admin-created bank found")
        
        bank_id = global_admin_bank.get('id')
        
        # Try to edit as parent - should fail with 403
        response = requests.put(f"{BASE_URL}/api/word-banks/{bank_id}",
            headers={"Authorization": f"Bearer {guardian_token}"},
            json={"description": "HACKED_BY_PARENT"})
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        print("Parent correctly forbidden from editing admin-created global bank")


class TestOtherParentCannotSeePrivateBank:
    """Test that other parents cannot see another parent's private bank"""
    
    def test_other_parent_cannot_see_first_parent_bank(self, guardian_token, other_guardian_token):
        """Other parent should NOT see the first parent's private word bank"""
        # Get first parent's banks to find their private bank
        response = requests.get(f"{BASE_URL}/api/word-banks",
            headers={"Authorization": f"Bearer {guardian_token}"})
        first_parent_banks = response.json()
        
        # Find first parent's private bank
        first_parent_private = next((b for b in first_parent_banks if b.get('created_by_role') == 'guardian' and b.get('visibility') == 'private'), None)
        if not first_parent_private:
            pytest.skip("First parent has no private bank")
        
        first_parent_bank_id = first_parent_private.get('id')
        first_parent_bank_name = first_parent_private.get('name')
        print(f"First parent has private bank: {first_parent_bank_name} (ID: {first_parent_bank_id})")
        
        # Get second parent's banks
        response = requests.get(f"{BASE_URL}/api/word-banks",
            headers={"Authorization": f"Bearer {other_guardian_token}"})
        assert response.status_code == 200
        second_parent_banks = response.json()
        
        # Check if first parent's private bank is visible to second parent
        visible_ids = [b.get('id') for b in second_parent_banks]
        assert first_parent_bank_id not in visible_ids, f"Other parent should NOT see first parent's private bank"
        print(f"Confirmed: Other parent does NOT see first parent's private bank '{first_parent_bank_name}'")
    
    def test_other_parent_sees_global_banks(self, other_guardian_token):
        """Other parent should still see global/marketplace banks"""
        response = requests.get(f"{BASE_URL}/api/word-banks",
            headers={"Authorization": f"Bearer {other_guardian_token}"})
        assert response.status_code == 200
        banks = response.json()
        
        global_banks = [b for b in banks if b.get('visibility') in ['global', 'marketplace']]
        print(f"Other parent sees {len(global_banks)} global/marketplace banks")
        assert len(global_banks) > 0, "Other parent should see at least some global banks"
    
    def test_other_parent_cannot_edit_first_parent_bank(self, guardian_token, other_guardian_token):
        """Other parent should NOT be able to edit first parent's private bank"""
        # Get first parent's private bank
        response = requests.get(f"{BASE_URL}/api/word-banks",
            headers={"Authorization": f"Bearer {guardian_token}"})
        first_parent_banks = response.json()
        
        first_parent_private = next((b for b in first_parent_banks if b.get('created_by_role') == 'guardian' and b.get('visibility') == 'private'), None)
        if not first_parent_private:
            pytest.skip("First parent has no private bank")
        
        bank_id = first_parent_private.get('id')
        
        # Try to edit as other parent - should fail with 403 or 404
        response = requests.put(f"{BASE_URL}/api/word-banks/{bank_id}",
            headers={"Authorization": f"Bearer {other_guardian_token}"},
            json={"description": "HACKED_BY_OTHER_PARENT"})
        # Could be 403 (not authorized) or 404 (not found in their visible list)
        assert response.status_code in [403, 404], f"Expected 403/404, got {response.status_code}: {response.text}"
        print("Other parent correctly forbidden from editing first parent's private bank")


class TestAdminSeesAllBanks:
    """Admin should see all banks including parent-created private ones"""
    
    def test_admin_sees_parent_private_banks(self, admin_token):
        """Admin can see parent-created private word banks"""
        response = requests.get(f"{BASE_URL}/api/word-banks",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        banks = response.json()
        
        parent_private_banks = [b for b in banks if b.get('created_by_role') == 'guardian' and b.get('visibility') == 'private']
        print(f"Admin sees {len(parent_private_banks)} parent-created private banks")
        
        # Admin should see all visibility types
        visibilities = set(b.get('visibility') for b in banks)
        print(f"Admin sees visibility types: {visibilities}")
        
        if 'private' in visibilities:
            print("Confirmed: Admin can see private word banks")
    
    def test_admin_can_edit_parent_private_bank(self, admin_token):
        """Admin can edit a parent-created private word bank"""
        response = requests.get(f"{BASE_URL}/api/word-banks",
            headers={"Authorization": f"Bearer {admin_token}"})
        banks = response.json()
        
        parent_bank = next((b for b in banks if b.get('created_by_role') == 'guardian'), None)
        if not parent_bank:
            pytest.skip("No parent-created bank found")
        
        bank_id = parent_bank.get('id')
        original_desc = parent_bank.get('description')
        
        # Admin edits parent's bank
        new_desc = "ADMIN_EDITED_" + (original_desc or "desc")
        response = requests.put(f"{BASE_URL}/api/word-banks/{bank_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"description": new_desc})
        assert response.status_code == 200
        updated = response.json()
        assert updated.get('description') == new_desc
        print("Admin successfully edited parent-created private bank")
        
        # Revert
        requests.put(f"{BASE_URL}/api/word-banks/{bank_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"description": original_desc})
        print("Reverted")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
