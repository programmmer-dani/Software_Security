# src/application/security/acl.py

from dataclasses import dataclass
from src.domain.errors import ValidationError
from src.domain.constants import ROLES

@dataclass
class CurrentUser:
    id: int
    role: str
    username_norm: str

def require_role(user: CurrentUser, allowed_roles: tuple):
    """Check if user has one of the allowed roles."""
    if user.role not in allowed_roles:
        raise ValidationError("Access denied. Insufficient permissions.")

def require_super_admin(user: CurrentUser):
    """Require SUPER_ADMIN role."""
    require_role(user, (ROLES[0],))  # SUPER_ADMIN

def require_admin(user: CurrentUser):
    """Require SUPER_ADMIN or SYS_ADMIN role."""
    require_role(user, (ROLES[0], ROLES[1]))  # SUPER_ADMIN, SYS_ADMIN

def require_engineer_or_admin(user: CurrentUser):
    """Require ENGINEER, SYS_ADMIN, or SUPER_ADMIN role."""
    require_role(user, ROLES)  # All roles
