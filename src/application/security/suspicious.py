

from datetime import datetime, timedelta
from collections import defaultdict, deque
from src.domain.policies import FAILED_LOGIN_THRESHOLD, FAILED_LOGIN_WINDOW_MINUTES

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

def clear_failed_logins(username: str):
    if username in _failed_logins:
        del _failed_logins[username]
