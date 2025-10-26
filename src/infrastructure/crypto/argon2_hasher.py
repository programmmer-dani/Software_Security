

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

MEMORY_COST = 65536
TIME_COST = 3
PARALLELISM = 1

_hasher = PasswordHasher(
    memory_cost=MEMORY_COST,
    time_cost=TIME_COST,
    parallelism=PARALLELISM,
    hash_len=32,
    salt_len=16
)

def hash(pw: str) -> str:
    if not pw or len(pw) < 12 or len(pw) > 30:
        raise ValueError("Password must be 12-30 characters")
    return _hasher.hash(pw)

def hash_token(token: str) -> str:

    if not token:
        raise ValueError("Token cannot be empty")
    return _hasher.hash(token)

def verify(pw: str, pw_hash: str) -> bool:
    try:
        return _hasher.verify(pw_hash, pw)
    except (VerifyMismatchError, Exception):
        return False
