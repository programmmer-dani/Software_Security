# src/domain/policies.py

from .constants import ROLES

# Suspicious detection thresholds
FAILED_LOGIN_THRESHOLD = 3
FAILED_LOGIN_WINDOW_MINUTES = 5

def can_create_sys_admin(role: str) -> bool:
    """Only SUPER_ADMIN can create system admins."""
    return role == ROLES[0]  # SUPER_ADMIN

def can_create_backup(role: str) -> bool:
    """SUPER_ADMIN or SYS_ADMIN can create backups."""
    return role in [ROLES[0], ROLES[1]]  # SUPER_ADMIN, SYS_ADMIN

def can_generate_restore_code(role: str) -> bool:
    """Only SUPER_ADMIN can generate restore codes."""
    return role == ROLES[0]  # SUPER_ADMIN

def can_restore_any_backup(role: str) -> bool:
    """Only SUPER_ADMIN can restore any backup directly (no restore code needed)."""
    return role == ROLES[0]  # SUPER_ADMIN

def can_restore_with_code(role: str) -> bool:
    """Only SYS_ADMIN can restore using a restore code."""
    return role == ROLES[1]  # SYS_ADMIN

def can_consume_restore_code(role: str) -> bool:
    """Only SYS_ADMIN can consume restore codes. SUPER_ADMIN cannot."""
    return role == ROLES[1]  # SYS_ADMIN only

def can_change_password(role: str) -> bool:
    """Super admin cannot change password, others can."""
    return role != ROLES[0]  # Not SUPER_ADMIN
