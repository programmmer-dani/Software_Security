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

print('\nSuper admin test completed!')
