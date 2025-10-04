# src/infrastructure/db/sqlite.py

import sqlite3
from pathlib import Path
from src.infrastructure.config import DATABASE_FILE
from src.domain.constants import ROLES

def get_conn():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA synchronous = NORMAL")
    return conn

def migrate():
    conn = get_conn()
    try:
        # Users table
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username_norm TEXT UNIQUE NOT NULL,
                username_enc TEXT NOT NULL,
                pw_hash TEXT NOT NULL,
                role TEXT CHECK(role IN ('{ROLES[0]}','{ROLES[1]}','{ROLES[2]}')) NOT NULL,
                first_name_enc TEXT NOT NULL,
                last_name_enc TEXT NOT NULL,
                registered_at TEXT NOT NULL
            )
        """)
        
        # Travellers table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS travellers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT UNIQUE NOT NULL,
                first_name_enc TEXT NOT NULL,
                last_name_enc TEXT NOT NULL,
                birthday TEXT NOT NULL,
                gender TEXT CHECK(gender IN ('male','female')) NOT NULL,
                street_enc TEXT NOT NULL,
                house_no_enc TEXT NOT NULL,
                zip_enc TEXT NOT NULL,
                city TEXT NOT NULL,
                email_enc TEXT NOT NULL,
                phone_enc TEXT NOT NULL,
                license_enc TEXT NOT NULL,
                registered_at TEXT NOT NULL
            )
        """)
        
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
        
        # Indexes
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_norm ON users(username_norm)")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_travellers_customer_id ON travellers(customer_id)")
        
        conn.commit()
        
        # Seed super_admin user if not exists
        _seed_super_admin(conn)
        conn.commit()
    finally:
        conn.close()

def _seed_super_admin(conn):
    cursor = conn.cursor()
    
    # Check if super_admin already exists
    cursor.execute("SELECT id FROM users WHERE username_norm = ?", ("super_admin",))
    if cursor.fetchone():
        return  # Already exists
    
    # Import here to avoid circular imports
    from src.infrastructure.crypto.fernet_box import encrypt
    from src.infrastructure.crypto.argon2_hasher import hash
    from datetime import datetime
    
    # Create super_admin user
    cursor.execute("""
        INSERT INTO users (username_norm, username_enc, pw_hash, role, first_name_enc, last_name_enc, registered_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "super_admin",
        encrypt("super_admin"),
        hash("Admin_123?!1"),
        ROLES[0],  # SUPER_ADMIN
        encrypt(""),
        encrypt(""),
        datetime.now().isoformat()
    ))
