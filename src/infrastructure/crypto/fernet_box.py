

import os
from cryptography.fernet import Fernet
from src.infrastructure.config import ENCRYPTION_KEY_FILE

def _get_key():
    if ENCRYPTION_KEY_FILE.exists():
        with open(ENCRYPTION_KEY_FILE, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        ENCRYPTION_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(ENCRYPTION_KEY_FILE, 'wb') as f:
            f.write(key)
        os.chmod(ENCRYPTION_KEY_FILE, 0o600)
        return key

_key = _get_key()
_fernet = Fernet(_key)

def encrypt(text: str) -> str:
    return _fernet.encrypt(text.encode()).decode()

def decrypt(ciphertext: str) -> str:
    return _fernet.decrypt(ciphertext.encode()).decode()

