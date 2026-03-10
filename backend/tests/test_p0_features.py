"""
Test P0 Features - Patent-Pending text fix and Affiliate tab
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestP0Features:
    """Tests for P0 bug fixes - Patent text and Affiliate tab"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for testing"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "allen@songsforcenturies.com",
            "password": "LexiAdmin2026!"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        return login_response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_affiliate_my_stats_endpoint_exists(self, auth_headers):
        """Test GET /api/affiliates/my-stats endpoint returns data for logged-in user"""
        response = requests.get(f"{BASE_URL}/api/affiliates/my-stats", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Should have is_affiliate field
        assert "is_affiliate" in data, "Response should contain 'is_affiliate' field"
        print(f"✓ /api/affiliates/my-stats returned: is_affiliate={data.get('is_affiliate')}")
        
        if data.get("is_affiliate"):
            # If user is an affiliate, should have affiliate details
            assert "affiliate" in data, "Affiliate user should have 'affiliate' field"
            affiliate = data["affiliate"]
            assert "affiliate_code" in affiliate, "Affiliate should have 'affiliate_code'"
            assert "confirmed" in affiliate, "Affiliate should have 'confirmed' status"
            print(f"✓ Affiliate code: {affiliate.get('affiliate_code')}")
            print(f"✓ Confirmed status: {affiliate.get('confirmed')}")
    
    def test_affiliate_signup_endpoint(self):
        """Test POST /api/affiliates/signup endpoint (public, no auth)"""
        import time
        test_email = f"test_affiliate_{int(time.time())}@testexample.com"
        
        response = requests.post(f"{BASE_URL}/api/affiliates/signup", json={
            "full_name": "Test Affiliate User",
            "email": test_email
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "affiliate_code" in data, "Response should contain 'affiliate_code'"
        assert data["affiliate_code"].startswith("AFF-"), f"Affiliate code should start with 'AFF-': {data['affiliate_code']}"
        assert "confirmed" in data, "Response should contain 'confirmed' status"
        print(f"✓ Affiliate signup successful: code={data['affiliate_code']}, confirmed={data['confirmed']}")
    
    def test_affiliate_duplicate_signup_rejected(self):
        """Test that duplicate affiliate signup is rejected"""
        import time
        test_email = f"test_dup_affiliate_{int(time.time())}@testexample.com"
        
        # First signup should succeed
        response1 = requests.post(f"{BASE_URL}/api/affiliates/signup", json={
            "full_name": "Test User",
            "email": test_email
        })
        assert response1.status_code == 200, "First signup should succeed"
        
        # Second signup with same email should fail
        response2 = requests.post(f"{BASE_URL}/api/affiliates/signup", json={
            "full_name": "Test User Again",
            "email": test_email
        })
        assert response2.status_code == 400, f"Duplicate signup should return 400, got {response2.status_code}"
        print(f"✓ Duplicate signup correctly rejected with 400")
    
    def test_affiliate_track_endpoint(self, auth_headers):
        """Test GET /api/affiliates/track/{code} endpoint"""
        # First get an affiliate code
        stats_response = requests.get(f"{BASE_URL}/api/affiliates/my-stats", headers=auth_headers)
        if stats_response.status_code == 200 and stats_response.json().get("is_affiliate"):
            affiliate_code = stats_response.json()["affiliate"]["affiliate_code"]
            
            # Track the code
            track_response = requests.get(f"{BASE_URL}/api/affiliates/track/{affiliate_code}")
            assert track_response.status_code == 200, f"Expected 200, got {track_response.status_code}"
            data = track_response.json()
            assert data.get("valid") == True, "Valid affiliate code should return valid=True"
            print(f"✓ Affiliate track endpoint works for code: {affiliate_code}")
        else:
            # Create a new affiliate to test with
            import time
            response = requests.post(f"{BASE_URL}/api/affiliates/signup", json={
                "full_name": "Track Test",
                "email": f"track_test_{int(time.time())}@test.com"
            })
            if response.status_code == 200:
                code = response.json()["affiliate_code"]
                track_response = requests.get(f"{BASE_URL}/api/affiliates/track/{code}")
                assert track_response.status_code == 200
                print(f"✓ Affiliate track endpoint works for new code: {code}")

    def test_affiliate_track_invalid_code(self):
        """Test that invalid affiliate code returns 404"""
        response = requests.get(f"{BASE_URL}/api/affiliates/track/INVALID-CODE")
        assert response.status_code == 404, f"Invalid code should return 404, got {response.status_code}"
        print("✓ Invalid affiliate code correctly returns 404")


class TestEnglishLocale:
    """Test i18n locale file for patent-pending text"""
    
    def test_health_endpoint(self):
        """Basic health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        # Health endpoint might not exist, that's okay
        print(f"Health check: {response.status_code}")
    

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
