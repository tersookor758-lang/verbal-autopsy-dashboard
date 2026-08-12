#!/usr/bin/env python3
import requests
import sys

base = 'http://localhost:5001'

# Test if Viewer can access GET endpoints
print("Testing RBAC: Viewer attempting PUT (should be 403 Forbidden)")
try:
    r = requests.post(f'{base}/api/auth/login', json={'username':'testviewer','password':'viewer123'})
    if r.status_code != 200:
        print(f"Login failed: {r.status_code}")
        sys.exit(1)
    viewer_token = r.json().get('access_token')
    
    # Try to PUT
    r = requests.put(f'{base}/api/verbal-autopsy/test', 
                     json={'state_name': 'Lagos'},
                     headers={'Authorization': f'Bearer {viewer_token}'})
    print(f"Viewer PUT /api/verbal-autopsy/test: Status {r.status_code}")
    print(f"Response: {r.json()}")
    
    if r.status_code == 403:
        print("✓ PASS: Viewer correctly denied PUT access (403)")
    else:
        print(f"✗ FAIL: Expected 403, got {r.status_code}")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
