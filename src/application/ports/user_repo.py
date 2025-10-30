

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class UserRepo(ABC):
    @abstractmethod
    def get_by_username_norm(self, username_norm: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def add(self, username_norm: str, pw_hash: str, role: str, first_name: str, last_name: str, registered_at: str) -> int:
        pass
    
    @abstractmethod
    def update_password(self, user_id: int, new_hash: str) -> None:
        pass
