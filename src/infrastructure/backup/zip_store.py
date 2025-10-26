

import zipfile
import shutil
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from src.infrastructure.config import DATABASE_FILE, BACKUP_FOLDER
from src.infrastructure.logging.sec_logger import log

def _create_selective_backup_db():

    import tempfile

    CORE_TABLES = ['users', 'travellers']
    
    def _validate_table_name(table_name: str) -> bool:

        return table_name in CORE_TABLES

    temp_fd, temp_path = tempfile.mkstemp(suffix='.db')
    temp_db = Path(temp_path)
    
    try:

        with sqlite3.connect(DATABASE_FILE) as source_conn:
            with sqlite3.connect(temp_db) as target_conn:

                for table in CORE_TABLES:

                    if not _validate_table_name(table):
                        raise ValueError(f"Invalid table name: {table}")

                    cursor = source_conn.cursor()
                    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
                    schema = cursor.fetchone()
                    
                    if schema:

                        target_conn.execute(schema[0])

                        cursor.execute(f"SELECT * FROM {table}")
                        rows = cursor.fetchall()
                        
                        if rows:

                            cursor.execute(f"PRAGMA table_info({table})")
                            columns = [col[1] for col in cursor.fetchall()]
                            placeholders = ','.join(['?' for _ in columns])

                            target_conn.executemany(f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})", rows)

                cursor = source_conn.cursor()
                cursor.execute("SELECT sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")
                indexes = cursor.fetchall()
                
                for index in indexes:
                    index_sql = index[0]

                    if any(table in index_sql for table in CORE_TABLES):
                        target_conn.execute(index_sql)
                
                target_conn.commit()
                
    except Exception as e:

        if temp_db.exists():
            temp_db.unlink()
        raise e
    finally:

        os.close(temp_fd)
    
    return temp_db

def _merge_restore_data(restored_db_path):

    from src.infrastructure.db.sqlite import get_conn

    session_backup = _backup_session_tables()
    
    try:

        with sqlite3.connect(restored_db_path) as restored_conn:

            _create_session_tables(restored_conn)

            if session_backup:
                _restore_session_tables(restored_conn, session_backup)
                
    except Exception as e:

        if session_backup and session_backup.exists():
            session_backup.unlink()
        raise e
    finally:

        if session_backup and session_backup.exists():
            session_backup.unlink()

def _backup_session_tables():

    import tempfile
    
    if not DATABASE_FILE.exists():
        return None
    
    temp_fd, temp_path = tempfile.mkstemp(suffix='.db')
    temp_db = Path(temp_path)
    
    try:
        with sqlite3.connect(DATABASE_FILE) as source_conn:
            with sqlite3.connect(temp_db) as target_conn:

                _create_session_tables(target_conn)

                SESSION_TABLES = ['restore_codes', 'log_state']
                
                def _validate_session_table_name(table_name: str) -> bool:

                    return table_name in SESSION_TABLES
                
                for table in SESSION_TABLES:

                    if not _validate_session_table_name(table):
                        raise ValueError(f"Invalid session table name: {table}")
                    
                    cursor = source_conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
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
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS log_state (
            user_id INTEGER PRIMARY KEY,
            last_seen_rowid INTEGER DEFAULT 0
        )
    """)

def _restore_session_tables(target_conn, session_backup_path):
    SESSION_TABLES = ['restore_codes', 'log_state']
    
    def _validate_session_table_name(table_name: str) -> bool:

        return table_name in SESSION_TABLES
    
    with sqlite3.connect(session_backup_path) as source_conn:
        for table in SESSION_TABLES:

            if not _validate_session_table_name(table):
                raise ValueError(f"Invalid session table name: {table}")
            
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

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{timestamp}_um.zip"
    backup_path = BACKUP_FOLDER / backup_name
    
    try:

        temp_db = _create_selective_backup_db()
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if temp_db.exists():
                zipf.write(temp_db, DATABASE_FILE.name)

        if temp_db.exists():
            temp_db.unlink()

        log('backup_created', 'system', {'backup_name': backup_name}, False)
        
        return backup_name
        
    except Exception as e:
        log('backup_failed', 'system', {'error': str(e)}, True)
        raise e

def restore_from_backup(backup_name: str):

    backup_path = BACKUP_FOLDER / backup_name

    if not backup_path.exists():
        log('restore_failed', 'system', {'backup_name': backup_name, 'reason': 'backup_not_found'}, True)
        raise FileNotFoundError(f"Backup {backup_name} not found")

    try:
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            if DATABASE_FILE.name not in zipf.namelist():
                log('restore_failed', 'system', {'backup_name': backup_name, 'reason': 'invalid_backup_format'}, True)
                raise ValueError(f"Backup {backup_name} does not contain database file")
    except zipfile.BadZipFile:
        log('restore_failed', 'system', {'backup_name': backup_name, 'reason': 'corrupted_backup'}, True)
        raise ValueError(f"Backup {backup_name} is corrupted or not a valid zip file")

    log('restore_started', 'system', {'backup_name': backup_name}, False)

    from src.infrastructure.db.sqlite import close_all_connections
    close_all_connections()

    temp_db = DATABASE_FILE.with_suffix('.tmp')
    
    try:

        with zipfile.ZipFile(backup_path, 'r') as zipf:
            with zipf.open(DATABASE_FILE.name) as source:
                with open(temp_db, 'wb') as target:
                    shutil.copyfileobj(source, target)

        temp_db_file = open(temp_db, 'rb+')
        temp_db_file.flush()
        os.fsync(temp_db_file.fileno())
        temp_db_file.close()

        _merge_restore_data(temp_db)

        if DATABASE_FILE.exists():
            DATABASE_FILE.unlink()
        
        shutil.move(str(temp_db), str(DATABASE_FILE))

        log('restore_completed', 'system', {'backup_name': backup_name}, False)
        
    except Exception as e:

        if temp_db.exists():
            temp_db.unlink()

        log('restore_failed', 'system', {'backup_name': backup_name, 'error': str(e)}, True)
        raise e
