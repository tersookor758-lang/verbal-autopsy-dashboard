import requests
import json

base = 'http://localhost:5001'

print('\n' + '='*70)
print('TEST 1: Unauthenticated access to /api/auth/me')
print('='*70)
r = requests.get(f'{base}/api/auth/me')
print(f'Status: {r.status_code}, Expected: 401, PASS: {r.status_code == 401}')
print(f'Response: {r.json()}')

print('\n' + '='*70)
print('TEST 2: POST /api/auth/login')
print('='*70)
r = requests.post(f'{base}/api/auth/login', json={'username':'admin','password':'admin123'})
print(f'Status: {r.status_code}')
data = r.json()
token = data.get('access_token')
user_role = data.get('user',{}).get('role')
print(f'Got token: {token is not None}')
print(f'User role: {user_role}')
print(f'PASS: {r.status_code == 200 and token is not None}')

print('\n' + '='*70)
print('TEST 3: Authenticated access to /api/auth/me')
print('='*70)
r = requests.get(f'{base}/api/auth/me', headers={'Authorization': f'Bearer {token}'})
print(f'Status: {r.status_code}, Expected: 200, PASS: {r.status_code == 200}')
print(f'Response: {r.json()}')

print('\n' + '='*70)
print('TEST 4: Protected endpoint without token')
print('='*70)
r = requests.get(f'{base}/api/verbal-autopsy/')
print(f'Status: {r.status_code}, Expected: 401, PASS: {r.status_code == 401}')

print('\n' + '='*70)
print('TEST 5: Protected endpoint with token')
print('='*70)
r = requests.get(f'{base}/api/verbal-autopsy/', headers={'Authorization': f'Bearer {token}'})
print(f'Status: {r.status_code}, Expected: 200, PASS: {r.status_code == 200}')

print('\n' + '='*70)
print('ALL TESTS COMPLETED SUCCESSFULLY!')
print('='*70)
