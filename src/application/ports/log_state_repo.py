# src/application/ports/log_state_repo.py

from abc import ABC, abstractmethod

class LogStateRepo(ABC):
    @abstractmethod
    def get_unread_suspicious_count(self, user_id: int) -> int:
        pass
    
    @abstractmethod
    def mark_all_seen(self, user_id: int) -> None:
        pass
