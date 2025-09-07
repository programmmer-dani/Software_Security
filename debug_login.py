#!/usr/bin/env python3

import sys
sys.path.append('src')

from domain.validators import validate_username
from infrastructure.db.user_repo_sqlite import get_by_username_norm
from infrastructure.crypto.argon2_hasher import verify

# Test step by step
print('Step 1: Validate username')
try:
    username_norm = validate_username('super_admin')
    print(f'Username normalized: {username_norm}')
except Exception as e:
    print(f'Username validation failed: {e}')

print('\nStep 2: Get user from database')
user = get_by_username_norm(username_norm)
print(f'User found: {user is not None}')
if user:
    print(f'User role: {user["role"]}')

print('\nStep 3: Verify password')
if user:
    password = 'Admin_123?!1'
    result = verify(password, user['pw_hash'])
    print(f'Password verification: {result}')

print('\nDebug completed')
