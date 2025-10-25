# src/infrastructure/db/sqlite.py

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from src.infrastructure.config import DATABASE_FILE
from src.domain.constants import ROLES

def get_conn():
    """Get a new database connection."""
    conn = sqlite3.connect(DATABASE_FILE)
    return conn

@contextmanager
def db_connection():
    """Context manager for database connections - automatically closes."""
    conn = get_conn()
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def db_transaction():
    """Context manager for database transactions - automatically commits/rollbacks."""
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def close_all_connections():
    """Force close all database connections to release file locks."""
    # SQLite doesn't provide a direct way to close all connections
    # This is mainly for backup/restore operations
    pass

def migrate():
    with db_transaction() as conn:
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
        
        # Scooters table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scooters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                serial_number TEXT UNIQUE NOT NULL,
                top_speed INTEGER NOT NULL,
                battery_capacity INTEGER NOT NULL,
                soc INTEGER CHECK(soc >= 0 AND soc <= 100) NOT NULL,
                target_soc_min INTEGER CHECK(target_soc_min >= 0 AND target_soc_min <= 100) NOT NULL,
                target_soc_max INTEGER CHECK(target_soc_max >= 0 AND target_soc_max <= 100) NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                out_of_service INTEGER CHECK(out_of_service IN (0,1)) NOT NULL,
                mileage INTEGER CHECK(mileage >= 0) NOT NULL,
                last_maintenance_date TEXT NOT NULL,
                in_service_date TEXT NOT NULL,
                status TEXT CHECK(status IN ('active','maintenance','retired')) NOT NULL
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
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_scooters_serial_number ON scooters(serial_number)")
        
        # Seed super_admin user if not exists
        _seed_super_admin(conn)

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
        "super_admin",  # Store as-is, no normalization
        encrypt("super_admin"),
        hash("Admin_123?"),
        ROLES[0],  # SUPER_ADMIN
        encrypt(""),
        encrypt(""),
        datetime.now().isoformat()
    ))
