# src/infrastructure/db/log_state_repo_sqlite.py

from .sqlite import db_connection, db_transaction
from src.infrastructure.logging.sec_logger import read_all

def get_unread_suspicious_count(user_id: int) -> int:
    with db_connection() as conn:
        cursor = conn.cursor()
        
        # Get last seen rowid for this user
        cursor.execute("SELECT last_seen_rowid FROM log_state WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        last_seen = row[0] if row else 0
        
        # Count unread suspicious events
        all_logs = read_all()
        count = 0
        for log_entry in all_logs:
            if log_entry['rowid'] > last_seen and log_entry['suspicious']:
                count += 1
        
        return count

def mark_all_seen(user_id: int):
    with db_transaction() as conn:
        cursor = conn.cursor()
        
        # Get latest rowid from logs
        all_logs = read_all()
        latest_rowid = max((log['rowid'] for log in all_logs), default=0)
        
        # Update or insert user's last seen rowid
        cursor.execute("""
            INSERT OR REPLACE INTO log_state (user_id, last_seen_rowid)
            VALUES (?, ?)
        """, (user_id, latest_rowid))
