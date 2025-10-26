

from src.application.ports.password_hasher import PasswordHasher
from src.infrastructure.crypto.argon2_hasher import hash, hash_token, verify

class PasswordHasherArgon2(PasswordHasher):
    def hash(self, password: str) -> str:
        return hash(password)
    
    def hash_token(self, token: str) -> str:
        return hash_token(token)
    
    def verify(self, password: str, password_hash: str) -> bool:
        return verify(password, password_hash)
