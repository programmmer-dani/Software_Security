# src/infrastructure/adapters/backup_store_zip.py

from src.application.ports.backup_store import BackupStore
from src.infrastructure.backup.zip_store import create_backup, restore_from_backup

class BackupStoreZip(BackupStore):
    def create_backup(self) -> str:
        return create_backup()
    
    def restore_from_backup(self, backup_name: str) -> None:
        return restore_from_backup(backup_name)
