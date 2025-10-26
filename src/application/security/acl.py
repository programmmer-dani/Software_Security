

from dataclasses import dataclass
from src.domain.errors import ValidationError
from src.domain.constants import ROLES

@dataclass
class CurrentUser:
    id: int
    role: str
    username_norm: str

def require_role(user: CurrentUser, allowed_roles: tuple):

    if user.role not in allowed_roles:
        raise ValidationError("Access denied. Insufficient permissions.")

def require_super_admin(user: CurrentUser):

    require_role(user, (ROLES[0],))

def require_admin(user: CurrentUser):

    require_role(user, (ROLES[0], ROLES[1]))

def require_engineer_or_admin(user: CurrentUser):

    require_role(user, ROLES)
