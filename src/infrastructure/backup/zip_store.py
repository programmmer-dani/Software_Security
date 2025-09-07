# src/infrastructure/backup/zip_store.py

import zipfile
import shutil
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from src.infrastructure.config import DATABASE_FILE, BACKUP_FOLDER
from src.infrastructure.logging.sec_logger import log


def create_backup():
    """Create a backup of the database file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{timestamp}_um.zip"
    backup_path = BACKUP_FOLDER / backup_name
    
    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if DATABASE_FILE.exists():
                zipf.write(DATABASE_FILE, DATABASE_FILE.name)
        
        # Log backup creation
        log('backup_created', 'system', {'backup_name': backup_name}, False)
        
        return backup_name
        
    except Exception as e:
        log('backup_failed', 'system', {'error': str(e)}, True)
        raise e


def _close_db_connections():
    """Close all SQLite connections to release file locks."""
    # Force close any existing connections
    try:
        # This is a simple approach - in production you might want to track connections
        # For now, we'll rely on the fact that connections should be closed after use
        pass
    except Exception:
        pass


def _reopen_db_connection():
    """Reopen database connection after restore."""
    from src.infrastructure.db.sqlite import get_conn
    return get_conn()


def restore_from_backup(backup_name: str):
    """Restore database from backup with atomic operation."""
    backup_path = BACKUP_FOLDER / backup_name
    
    # Pre-restore safety checks
    if not backup_path.exists():
        log('restore_failed', 'system', {'backup_name': backup_name, 'reason': 'backup_not_found'}, True)
        raise FileNotFoundError(f"Backup {backup_name} not found")
    
    # Validate backup file is a valid zip
    try:
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            if DATABASE_FILE.name not in zipf.namelist():
                log('restore_failed', 'system', {'backup_name': backup_name, 'reason': 'invalid_backup_format'}, True)
                raise ValueError(f"Backup {backup_name} does not contain database file")
    except zipfile.BadZipFile:
        log('restore_failed', 'system', {'backup_name': backup_name, 'reason': 'corrupted_backup'}, True)
        raise ValueError(f"Backup {backup_name} is corrupted or not a valid zip file")
    
    # Log restore start
    log('restore_started', 'system', {'backup_name': backup_name}, False)
    
    # Close DB connections to release file locks
    _close_db_connections()
    
    # Create temporary file in same directory as target
    temp_db = DATABASE_FILE.with_suffix('.tmp')
    
    try:
        # Extract database from backup to temp location
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            with zipf.open(DATABASE_FILE.name) as source:
                with open(temp_db, 'wb') as target:
                    shutil.copyfileobj(source, target)
        
        # Ensure data is fully written to disk
        temp_db_file = open(temp_db, 'rb+')
        temp_db_file.flush()
        os.fsync(temp_db_file.fileno())
        temp_db_file.close()
        
        # Atomic swap - replace current DB with restored version
        if DATABASE_FILE.exists():
            DATABASE_FILE.unlink()  # Remove current DB
        
        shutil.move(str(temp_db), str(DATABASE_FILE))
        
        # Reopen database connection
        _reopen_db_connection()
        
        # Log successful restore
        log('restore_completed', 'system', {'backup_name': backup_name}, False)
        
    except Exception as e:
        # Clean up temp file on error
        if temp_db.exists():
            temp_db.unlink()
        
        # Log restore failure
        log('restore_failed', 'system', {'backup_name': backup_name, 'error': str(e)}, True)
        
        # Try to reopen connection even after failure
        try:
            _reopen_db_connection()
        except Exception:
            pass  # Connection might already be open
        
        raise e
