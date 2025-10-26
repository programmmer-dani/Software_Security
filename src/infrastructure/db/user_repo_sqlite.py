

from .sqlite import db_connection
from src.infrastructure.crypto.fernet_box import encrypt, decrypt

def get_by_username_norm(username_norm: str):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username_norm = ?", (username_norm,))
        row = cursor.fetchone()
        
        if not row:
            return None

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
            encrypt(username_norm),
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
        return cursor.rowcount > 0

def update_profile(user_id: int, **kwargs):
    from .sqlite import db_transaction
    with db_transaction() as conn:
        cursor = conn.cursor()
        
        if not kwargs:
            return False
        
        set_clauses = []
        values = []
        
        for key, value in kwargs.items():
            if key == 'first_name':
                set_clauses.append('first_name_enc = ?')
                values.append(encrypt(value))
            elif key == 'last_name':
                set_clauses.append('last_name_enc = ?')
                values.append(encrypt(value))
        
        if not set_clauses:
            return False
        
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?"
        cursor.execute(query, values)
        
        return cursor.rowcount > 0

def delete(user_id: int):
    from .sqlite import db_transaction
    with db_transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return cursor.rowcount > 0
