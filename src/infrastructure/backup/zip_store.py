# src/infrastructure/backup/zip_store.py

import zipfile
import shutil
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from src.infrastructure.config import DATABASE_FILE, BACKUP_FOLDER
from src.infrastructure.logging.sec_logger import log


def _create_selective_backup_db():
    """Create a temporary database with only core business data (excludes restore_codes and log_state)."""
    import sqlite3
    import tempfile
    
    # Tables to include in backup (core business data)
    CORE_TABLES = ['users', 'travellers']
    
    # Create temporary database
    temp_fd, temp_path = tempfile.mkstemp(suffix='.db')
    temp_db = Path(temp_path)
    
    try:
        # Connect to original and temporary databases
        with sqlite3.connect(DATABASE_FILE) as source_conn:
            with sqlite3.connect(temp_db) as target_conn:
                # Copy schema for core tables
                for table in CORE_TABLES:
                    # Get table schema
                    cursor = source_conn.cursor()
                    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
                    schema = cursor.fetchone()
                    
                    if schema:
                        # Create table in target database
                        target_conn.execute(schema[0])
                        
                        # Copy data
                        cursor.execute(f"SELECT * FROM {table}")
                        rows = cursor.fetchall()
                        
                        if rows:
                            # Get column names
                            cursor.execute(f"PRAGMA table_info({table})")
                            columns = [col[1] for col in cursor.fetchall()]
                            placeholders = ','.join(['?' for _ in columns])
                            
                            # Insert data
                            target_conn.executemany(f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})", rows)
                
                # Copy indexes for core tables
                cursor = source_conn.cursor()
                cursor.execute("SELECT sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")
                indexes = cursor.fetchall()
                
                for index in indexes:
                    index_sql = index[0]
                    # Only copy indexes for core tables
                    if any(table in index_sql for table in CORE_TABLES):
                        target_conn.execute(index_sql)
                
                target_conn.commit()
                
    except Exception as e:
        # Clean up on error
        if temp_db.exists():
            temp_db.unlink()
        raise e
    finally:
        # Close file descriptor
        os.close(temp_fd)
    
    return temp_db


def _merge_restore_data(restored_db_path):
    """Merge restored core data with fresh session tables (restore_codes, log_state)."""
    import sqlite3
    from src.infrastructure.db.sqlite import get_conn
    
    # Create a backup of current session data before restore
    session_backup = _backup_session_tables()
    
    try:
        # Connect to both databases
        with sqlite3.connect(restored_db_path) as restored_conn:
            # Create missing session tables in restored database
            _create_session_tables(restored_conn)
            
            # Restore session data if it exists
            if session_backup:
                _restore_session_tables(restored_conn, session_backup)
                
    except Exception as e:
        # Clean up session backup on error
        if session_backup and session_backup.exists():
            session_backup.unlink()
        raise e
    finally:
        # Clean up session backup
        if session_backup and session_backup.exists():
            session_backup.unlink()


def _backup_session_tables():
    """Backup current session tables to temporary file."""
    import sqlite3
    import tempfile
    
    if not DATABASE_FILE.exists():
        return None
    
    temp_fd, temp_path = tempfile.mkstemp(suffix='.db')
    temp_db = Path(temp_path)
    
    try:
        with sqlite3.connect(DATABASE_FILE) as source_conn:
            with sqlite3.connect(temp_db) as target_conn:
                # Create session tables in backup
                _create_session_tables(target_conn)
                
                # Copy session data
                SESSION_TABLES = ['restore_codes', 'log_state']
                for table in SESSION_TABLES:
                    cursor = source_conn.cursor()
                    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                    if cursor.fetchone():
                        cursor.execute(f"SELECT * FROM {table}")
                        rows = cursor.fetchall()
                        
                        if rows:
                            cursor.execute(f"PRAGMA table_info({table})")
                            columns = [col[1] for col in cursor.fetchall()]
                            placeholders = ','.join(['?' for _ in columns])
                            target_conn.executemany(f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})", rows)
                
                target_conn.commit()
                
    except Exception as e:
        if temp_db.exists():
            temp_db.unlink()
        os.close(temp_fd)
        return None
    finally:
        os.close(temp_fd)
    
    return temp_db


def _create_session_tables(conn):
    """Create session tables (restore_codes, log_state) in database."""
    # Restore codes table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS restore_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            backup_name TEXT NOT NULL,
            granted_to_user_id INTEGER NOT NULL,
            code_hash TEXT NOT NULL,
            used INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    
    # Log state table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS log_state (
            user_id INTEGER PRIMARY KEY,
            last_seen_rowid INTEGER DEFAULT 0
        )
    """)
    
    conn.commit()


def _restore_session_tables(target_conn, session_backup_path):
    """Restore session tables from backup."""
    import sqlite3
    
    SESSION_TABLES = ['restore_codes', 'log_state']
    
    with sqlite3.connect(session_backup_path) as source_conn:
        for table in SESSION_TABLES:
            cursor = source_conn.cursor()
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            if rows:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                placeholders = ','.join(['?' for _ in columns])
                target_conn.executemany(f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})", rows)
        
        target_conn.commit()


def create_backup():
    """Create a selective backup excluding session-specific tables."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{timestamp}_um.zip"
    backup_path = BACKUP_FOLDER / backup_name
    
    try:
        # Create a temporary database with only core business data
        temp_db = _create_selective_backup_db()
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if temp_db.exists():
                zipf.write(temp_db, DATABASE_FILE.name)
        
        # Clean up temporary file
        if temp_db.exists():
            temp_db.unlink()
        
        # Log backup creation
        log('backup_created', 'system', {'backup_name': backup_name}, False)
        
        return backup_name
        
    except Exception as e:
        log('backup_failed', 'system', {'error': str(e)}, True)
        raise e




def restore_from_backup(backup_name: str):
    """Restore database from selective backup with proper table handling."""
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
    from src.infrastructure.db.sqlite import close_all_connections
    close_all_connections()
    
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
        
        # Merge restored data with existing session tables
        _merge_restore_data(temp_db)
        
        # Atomic swap - replace current DB with merged version
        if DATABASE_FILE.exists():
            DATABASE_FILE.unlink()  # Remove current DB
        
        shutil.move(str(temp_db), str(DATABASE_FILE))
        
        # Log successful restore
        log('restore_completed', 'system', {'backup_name': backup_name}, False)
        
    except Exception as e:
        # Clean up temp file on error
        if temp_db.exists():
            temp_db.unlink()
        
        # Log restore failure
        log('restore_failed', 'system', {'backup_name': backup_name, 'error': str(e)}, True)
        
        # Database connections will be reopened automatically when needed
        
        raise e
