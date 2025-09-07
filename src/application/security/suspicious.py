# src/application/security/suspicious.py

from datetime import datetime, timedelta
from collections import defaultdict, deque

# Suspicious detection thresholds
FAILED_LOGIN_THRESHOLD = 3
FAILED_LOGIN_WINDOW_MINUTES = 5

# In-memory tracking of failed logins
_failed_logins = defaultdict(lambda: deque())

def _clean_old_attempts(username: str):
    now = datetime.now()
    cutoff = now - timedelta(minutes=FAILED_LOGIN_WINDOW_MINUTES)
    
    attempts = _failed_logins[username]
    while attempts and attempts[0] < cutoff:
        attempts.popleft()

def is_failed_login_suspicious(username: str) -> bool:
    _clean_old_attempts(username)
    attempts = _failed_logins[username]
    
    return len(attempts) >= FAILED_LOGIN_THRESHOLD

def record_failed_login(username: str):
    now = datetime.now()
    _failed_logins[username].append(now)

def is_restore_attempt_suspicious(success: bool) -> bool:
    return not success

def clear_failed_logins(username: str):
    if username in _failed_logins:
        del _failed_logins[username]
