

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime
from src.infrastructure.config import DATABASE_FILE
from src.domain.constants import ROLES
from src.infrastructure.crypto.fernet_box import encrypt

def get_conn():

    conn = sqlite3.connect(DATABASE_FILE)
    return conn

@contextmanager
def db_connection():

    conn = get_conn()
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def db_transaction():

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

    pass

def migrate():
    with db_transaction() as conn:

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

            CREATE TABLE IF NOT EXISTS restore_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_name TEXT NOT NULL,
                granted_to_user_id INTEGER NOT NULL,
                code_hash TEXT NOT NULL,
                used INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )

            CREATE TABLE IF NOT EXISTS log_state (
                user_id INTEGER PRIMARY KEY,
                last_seen_rowid INTEGER DEFAULT 0
            )

        INSERT INTO users (username_norm, username_enc, pw_hash, role, first_name_enc, last_name_enc, registered_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "super_admin",
        encrypt("super_admin"),
        hash("Admin_123?"),
        ROLES[0],
        encrypt(""),
        encrypt(""),
        datetime.now().isoformat()
    ))
