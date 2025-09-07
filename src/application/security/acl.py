# src/application/security/acl.py

from dataclasses import dataclass

@dataclass
class CurrentUser:
    id: int
    role: str
    username_norm: str
