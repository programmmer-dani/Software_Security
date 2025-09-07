#!/usr/bin/env python3

import sys
sys.path.append('src')

from infrastructure.db.user_repo_sqlite import get_by_username_norm
from infrastructure.crypto.argon2_hasher import verify

user = get_by_username_norm('super_admin')
print(f'User found: {user is not None}')
if user:
    print(f'Role: {user["role"]}')
    # Test password verification
    test_passwords = ['Admin_123?!1', 'Admin_123?!', 'Admin_123?']
    for pwd in test_passwords:
        try:
            result = verify(pwd, user['pw_hash'])
            print(f'Password "{pwd}" verification: {result}')
        except Exception as e:
            print(f'Password "{pwd}" error: {e}')
