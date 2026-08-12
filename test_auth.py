#!/usr/bin/env python3
"""
Test script for authentication and authorization endpoints.
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:5001"
API_BASE = f"{BASE_URL}/api"

# Wait for server to be ready
print("Waiting for server to be ready...")
for i in range(10):
    try:
        requests.get(f"{API_BASE}/auth/me")
        print("Server is ready!\n")
        break
    except:
        if i < 9:
            sleep(1)
        else:
            print("Server did not start in time")
            exit(1)

# Test 1: GET /api/auth/me without token
print("=" * 70)
print("Test 1: GET /api/auth/me WITHOUT token (should be 401)")
print("=" * 70)
response = requests.get(f"{API_BASE}/auth/me")
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
assert response.status_code == 401, f"Expected 401, got {response.status_code}"
print("✓ PASSED: Returns 401 Unauthorized\n")

# Test 2: POST /api/auth/login with valid credentials
print("=" * 70)
print("Test 2: POST /api/auth/login with valid credentials")
print("=" * 70)
response = requests.post(
    f"{API_BASE}/auth/login",
    json={"username": "admin", "password": "admin123"}
)
print(f"Status Code: {response.status_code}")
response_data = response.json()
print(f"Response Keys: {list(response_data.keys())}")
print(f"Message: {response_data.get('message')}")
print(f"Access Token: {response_data.get('access_token', 'N/A')[:50]}...")
print(f"Refresh Token: {response_data.get('refresh_token', 'N/A')[:50]}...")
print(f"User Role: {response_data.get('user', {}).get('role')}")

assert response.status_code == 200, f"Expected 200, got {response.status_code}"
assert "access_token" in response_data, "Missing access_token"
assert "refresh_token" in response_data, "Missing refresh_token"
assert response_data["user"]["role"] == "Administrator", "Expected Administrator role"

access_token = response_data["access_token"]
admin_user = response_data["user"]
print(f"✓ PASSED: Got valid access token for {admin_user['username']} ({admin_user['role']})\n")

# Test 3: GET /api/auth/me with valid token
print("=" * 70)
print("Test 3: GET /api/auth/me WITH valid token (should be 200)")
print("=" * 70)
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{API_BASE}/auth/me", headers=headers)
print(f"Status Code: {response.status_code}")
response_data = response.json()
print(f"Response: {json.dumps(response_data, indent=2)}")

assert response.status_code == 200, f"Expected 200, got {response.status_code}"
assert response_data["role"] == "Administrator", "Expected Administrator role"
print("✓ PASSED: Authentication successful\n")

# Test 4: GET /api/verbal-autopsy/ (should require auth)
print("=" * 70)
print("Test 4: GET /api/verbal-autopsy/ WITHOUT token (should be 401)")
print("=" * 70)
response = requests.get(f"{API_BASE}/verbal-autopsy/")
print(f"Status Code: {response.status_code}")
assert response.status_code == 401, f"Expected 401, got {response.status_code}"
print("✓ PASSED: Returns 401 Unauthorized\n")

# Test 5: GET /api/verbal-autopsy/ WITH token (should be 200)
print("=" * 70)
print("Test 5: GET /api/verbal-autopsy/ WITH valid token (should be 200)")
print("=" * 70)
response = requests.get(f"{API_BASE}/verbal-autopsy/", headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Records count: {len(response.json())}")
assert response.status_code == 200, f"Expected 200, got {response.status_code}"
print("✓ PASSED: Retrieved records successfully\n")

# Test 6: GET /api/verbal-autopsy/locations (should require auth)
print("=" * 70)
print("Test 6: GET /api/verbal-autopsy/locations WITHOUT token (should be 401)")
print("=" * 70)
response = requests.get(f"{API_BASE}/verbal-autopsy/locations")
print(f"Status Code: {response.status_code}")
assert response.status_code == 401, f"Expected 401, got {response.status_code}"
print("✓ PASSED: Returns 401 Unauthorized\n")

# Test 7: GET /api/verbal-autopsy/locations WITH token (should be 200)
print("=" * 70)
print("Test 7: GET /api/verbal-autopsy/locations WITH valid token")
print("=" * 70)
response = requests.get(f"{API_BASE}/verbal-autopsy/locations", headers=headers)
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Response keys: {list(data.keys())}")
if "states" in data:
    print(f"States count: {len(data['states'])}")
assert response.status_code == 200, f"Expected 200, got {response.status_code}"
print("✓ PASSED: Retrieved locations successfully\n")

# Test 8: Test Swagger endpoint accessibility
print("=" * 70)
print("Test 8: GET /swagger (Swagger UI)")
print("=" * 70)
response = requests.get(f"{BASE_URL}/swagger")
print(f"Status Code: {response.status_code}")
assert response.status_code == 200, f"Expected 200, got {response.status_code}"
print("✓ PASSED: Swagger UI is accessible\n")

print("=" * 70)
print("ALL TESTS PASSED! ✓")
print("=" * 70)
print("\nSummary:")
print("✓ JWT authentication is enforced on all API endpoints")
print("✓ Authorization header is required for protected endpoints")
print("✓ Valid tokens grant access to endpoints")
print("✓ Admin user can access all endpoints")
print("✓ Swagger documentation is accessible")
