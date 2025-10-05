# src/infrastructure/db/user_repo_sqlite.py

from datetime import datetime
from .sqlite import db_connection
from src.infrastructure.crypto.fernet_box import encrypt, decrypt

def get_by_username_norm(username_norm: str):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username_norm = ?", (username_norm,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Decrypt sensitive fields
        return {
            'id': row[0],
            'username_norm': row[1],
            'username': decrypt(row[2]),
            'pw_hash': row[3],
            'role': row[4],
            'first_name': decrypt(row[5]),
            'last_name': decrypt(row[6]),
            'registered_at': row[7]
        }

def add(username_norm: str, pw_hash: str, role: str, first_name: str, last_name: str, registered_at: str):
    from .sqlite import db_transaction
    with db_transaction() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (username_norm, username_enc, pw_hash, role, first_name_enc, last_name_enc, registered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            username_norm,
            encrypt(username_norm),  # Use normalized username for encryption
            pw_hash,
            role,
            encrypt(first_name),
            encrypt(last_name),
            registered_at
        ))
        
        return cursor.lastrowid

def update_password(user_id: int, new_hash: str):
    from .sqlite import db_transaction
    with db_transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET pw_hash = ? WHERE id = ?", (new_hash, user_id))
