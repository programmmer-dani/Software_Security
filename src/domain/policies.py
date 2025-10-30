

from .constants import ROLES

FAILED_LOGIN_THRESHOLD = 3
FAILED_LOGIN_WINDOW_MINUTES = 5

def can_create_sys_admin(role: str) -> bool:

    return role == ROLES[0]

def can_create_backup(role: str) -> bool:

    return role in [ROLES[0], ROLES[1]]

def can_generate_restore_code(role: str) -> bool:

    return role == ROLES[0]

def can_restore_any_backup(role: str) -> bool:

    return False

def can_restore_with_code(role: str) -> bool:

    return role == ROLES[1]

def can_consume_restore_code(role: str) -> bool:

    return role == ROLES[1]

def can_change_password(role: str) -> bool:

    return role != ROLES[0]
