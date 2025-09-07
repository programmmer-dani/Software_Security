#!/usr/bin/env python3

import sys
sys.path.append('src')

from application.use_cases.auth import login, change_password

# Test super_admin login
print('Testing super_admin login...')
try:
    super_admin = login('super_admin', 'Admin_123?!1')
    print(f'Super admin login successful: {super_admin.username_norm} ({super_admin.role})')
except Exception as e:
    print(f'Super admin login failed: {e}')

# Test super_admin password change (should be blocked)
print('\nTesting super_admin password change (should be blocked)...')
try:
    change_password(super_admin, 'Admin_123?!1', 'NewPassword123!')
    print('ERROR: Super admin password change should be blocked')
except Exception as e:
    print(f'Super admin password change correctly blocked: {e}')

# Test regular user password change (should work)
print('\nTesting regular user password change...')
try:
    # Create a regular user for testing
    from infrastructure.db.user_repo_sqlite import add as add_user
    from infrastructure.crypto.argon2_hasher import hash
    add_user('RegularUser', hash('password123!'), 'ENGINEER', 'Regular', 'User')
    
    regular_user = login('RegularUser', 'password123!')
    change_password(regular_user, 'password123!', 'NewPassword123!')
    print('Regular user password change successful')
except Exception as e:
    print(f'Regular user password change failed: {e}')

print('\nSuper admin seeding test completed!')
