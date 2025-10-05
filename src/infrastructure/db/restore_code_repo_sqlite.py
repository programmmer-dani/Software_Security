# src/infrastructure/db/restore_code_repo_sqlite.py

from datetime import datetime
from .sqlite import db_connection, db_transaction
from src.infrastructure.crypto.argon2_hasher import verify

def insert(backup_name: str, user_id: int, code_hash: str):
    with db_transaction() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO restore_codes (backup_name, granted_to_user_id, code_hash, used, created_at)
            VALUES (?, ?, ?, 0, ?)
        """, (backup_name, user_id, code_hash, datetime.now().isoformat()))
        
        return cursor.lastrowid

def consume(user_id: int, backup_name: str, candidate_code: str):
    with db_transaction() as conn:
        cursor = conn.cursor()
        
        # Find unused codes for this user and backup
        cursor.execute("""
            SELECT id, code_hash FROM restore_codes 
            WHERE granted_to_user_id = ? AND backup_name = ? AND used = 0
        """, (user_id, backup_name))
        
        rows = cursor.fetchall()
        
        # Check each code
        for row in rows:
            code_id, stored_hash = row
            if verify(candidate_code, stored_hash):
                # Mark as used atomically
                cursor.execute("UPDATE restore_codes SET used = 1 WHERE id = ?", (code_id,))
                return True
        
        return False
