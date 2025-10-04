# src/application/ports/backup_store.py

from abc import ABC, abstractmethod

class BackupStore(ABC):
    @abstractmethod
    def create_backup(self) -> str:
        pass
    
    @abstractmethod
    def restore_from_backup(self, backup_name: str) -> None:
        pass
