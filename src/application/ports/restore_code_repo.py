

from abc import ABC, abstractmethod

class RestoreCodeRepo(ABC):
    @abstractmethod
    def insert(self, backup_name: str, user_id: int, code_hash: str) -> int:
        pass
    
    @abstractmethod
    def consume(self, user_id: int, backup_name: str, candidate_code: str) -> bool:
        pass
