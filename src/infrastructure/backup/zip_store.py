# src/infrastructure/backup/zip_store.py

import zipfile
import shutil
from datetime import datetime
from pathlib import Path
from src.infrastructure.config import DATABASE_FILE, BACKUP_FOLDER


def create_backup():
    """Create a backup of the database file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{timestamp}_um.zip"
    backup_path = BACKUP_FOLDER / backup_name
    
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if DATABASE_FILE.exists():
            zipf.write(DATABASE_FILE, DATABASE_FILE.name)
    
    return backup_name


def restore_from_backup(backup_name: str):
    """Restore database from backup."""
    backup_path = BACKUP_FOLDER / backup_name
    
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup {backup_name} not found")
    
    # Create temporary file
    temp_db = DATABASE_FILE.with_suffix('.tmp')
    
    try:
        # Extract database from backup
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extract(DATABASE_FILE.name, temp_db.parent)
        
        # Move extracted file to temp location
        extracted_db = temp_db.parent / DATABASE_FILE.name
        if extracted_db.exists():
            shutil.move(str(extracted_db), str(temp_db))
        
        # Atomic swap
        if temp_db.exists():
            shutil.move(str(temp_db), str(DATABASE_FILE))
            
    except Exception as e:
        # Clean up temp file on error
        if temp_db.exists():
            temp_db.unlink()
        raise e
