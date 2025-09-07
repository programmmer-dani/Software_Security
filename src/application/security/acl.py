# src/application/security/acl.py

from dataclasses import dataclass
from src.domain.errors import ValidationError

@dataclass
class CurrentUser:
    id: int
    role: str
    username_norm: str

def require_role(*allowed_roles):
    def decorator(func):
        def wrapper(current_user: CurrentUser, *args, **kwargs):
            if current_user.role not in allowed_roles:
                raise ValidationError("Access denied: insufficient permissions")
            return func(current_user, *args, **kwargs)
        return wrapper
    return decorator

def check_role(current_user: CurrentUser, *allowed_roles) -> bool:
    return current_user.role in allowed_roles

def is_super_admin(current_user: CurrentUser) -> bool:
    return current_user.role == 'SUPER_ADMIN'

def is_sys_admin(current_user: CurrentUser) -> bool:
    return current_user.role in ['SUPER_ADMIN', 'SYS_ADMIN']

def is_engineer(current_user: CurrentUser) -> bool:
    return current_user.role in ['SUPER_ADMIN', 'SYS_ADMIN', 'ENGINEER']
