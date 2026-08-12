"""
Quick integration test for Phase 3 security hardening.

Tests the actual endpoints without waiting for rate limit resets.
"""

import requests
import time
import json

BASE_URL = "http://127.0.0.1:5001"

def test_endpoint(method, url, data=None, headers=None, expected_status=None):
    """Helper to test an endpoint."""
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            resp = requests.post(url, json=data, headers=headers, timeout=5)
        else:
            return None
        
        return resp
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("="*60)
    print("PHASE 3 INTEGRATION TEST (Quick Run)")
    print("="*60)
    
    print("\nTest 1: Login and get tokens")
    resp = test_endpoint("POST", f"{BASE_URL}/api/auth/login", 
                        {"username": "admin", "password": "admin123"})
    
    if resp and resp.status_code == 200:
        print("✓ Login successful (200)")
        login_data = resp.json()
        access_token = login_data.get("access_token")
        refresh_token = login_data.get("refresh_token")
        print(f"  Access token: {access_token[:30]}...")
        print(f"  Refresh token: {refresh_token[:30]}...")
    else:
        print(f"✗ Login failed: {resp.status_code if resp else 'No response'}")
        if resp:
            print(f"  Response: {resp.json()}")
        return
    
    print("\nTest 2: Get current user")
    resp = test_endpoint("GET", f"{BASE_URL}/api/auth/me",
                        headers={"Authorization": f"Bearer {access_token}"})
    
    if resp and resp.status_code == 200:
        print("✓ Get /api/auth/me successful (200)")
        user_data = resp.json()
        print(f"  User: {user_data.get('username')} (Role: {user_data.get('role')})")
    else:
        print(f"✗ Get user failed: {resp.status_code if resp else 'No response'}")
    
    print("\nTest 3: Unauthorized access (no token)")
    resp = test_endpoint("GET", f"{BASE_URL}/api/auth/me")
    
    if resp and resp.status_code == 401:
        print("✓ Unauthorized access properly rejected (401)")
    else:
        print(f"✗ Expected 401, got: {resp.status_code if resp else 'No response'}")
    
    print("\nTest 4: Refresh token")
    resp = test_endpoint("POST", f"{BASE_URL}/api/auth/refresh",
                        {"refresh_token": refresh_token})
    
    if resp and resp.status_code == 200:
        print("✓ Token refresh successful (200)")
        new_data = resp.json()
        new_access_token = new_data.get("access_token")
        new_refresh_token = new_data.get("refresh_token")
        print(f"  New access token: {new_access_token[:30]}...")
        print(f"  New refresh token: {new_refresh_token[:30]}...")
        
        # Verify old token is revoked
        print("\nTest 5: Old refresh token revoked")
        resp2 = test_endpoint("POST", f"{BASE_URL}/api/auth/refresh",
                             {"refresh_token": refresh_token})
        
        if resp2 and resp2.status_code == 401:
            print("✓ Old refresh token properly revoked (401)")
        else:
            print(f"✗ Old token should be rejected: {resp2.status_code if resp2 else 'No response'}")
    else:
        print(f"✗ Token refresh failed: {resp.status_code if resp else 'No response'}")
        if resp:
            print(f"  Response: {resp.json()}")
    
    print("\nTest 6: Logout")
    # Need a fresh token for logout
    resp_login = test_endpoint("POST", f"{BASE_URL}/api/auth/login",
                              {"username": "admin", "password": "admin123"})
    
    if resp_login and resp_login.status_code == 200:
        logout_refresh = resp_login.json().get("refresh_token")
        
        resp = test_endpoint("POST", f"{BASE_URL}/api/auth/logout",
                            {"refresh_token": logout_refresh})
        
        if resp and resp.status_code == 200:
            print("✓ Logout successful (200)")
            
            # Verify token is revoked
            resp2 = test_endpoint("POST", f"{BASE_URL}/api/auth/refresh",
                                 {"refresh_token": logout_refresh})
            
            if resp2 and resp2.status_code == 401:
                print("✓ Token revoked after logout (401)")
            else:
                print(f"✗ Token should be revoked: {resp2.status_code if resp2 else 'No response'}")
        else:
            print(f"✗ Logout failed: {resp.status_code if resp else 'No response'}")
    
    print("\nTest 7: Revoke-all tokens endpoint")
    # Need a fresh token
    resp_login = test_endpoint("POST", f"{BASE_URL}/api/auth/login",
                              {"username": "admin", "password": "admin123"})
    
    if resp_login and resp_login.status_code == 200:
        revoke_token = resp_login.json().get("access_token")
        
        resp = test_endpoint("POST", f"{BASE_URL}/api/auth/revoke-all",
                            headers={"Authorization": f"Bearer {revoke_token}"})
        
        if resp and resp.status_code == 200:
            print("✓ Revoke-all endpoint successful (200)")
            print(f"  Message: {resp.json().get('message')}")
        else:
            print(f"✗ Revoke-all failed: {resp.status_code if resp else 'No response'}")
            if resp:
                print(f"  Response: {resp.json()}")
    
    print("\n" + "="*60)
    print("Integration test complete!")
    print("="*60)

if __name__ == "__main__":
    main()
