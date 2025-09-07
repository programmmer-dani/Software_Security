# src/infrastructure/logging/sec_logger.py

import json
from datetime import datetime
from pathlib import Path
from infrastructure.config import ENCRYPTION_LOGS_FILE
from infrastructure.crypto.fernet_box import encrypt, decrypt

_rowid_counter = 0

def _get_next_rowid():
    global _rowid_counter
    _rowid_counter += 1
    return _rowid_counter

def log(event: str, user: str = None, details: dict = None, suspicious: bool = False):
    record = {
        'ts': datetime.now().isoformat(),
        'user': user,
        'event': event,
        'details': details or {},
        'suspicious': suspicious,
        'rowid': _get_next_rowid()
    }
    
    json_line = json.dumps(record)
    encrypted_line = encrypt(json_line)
    
    with open(ENCRYPTION_LOGS_FILE, 'a') as f:
        f.write(encrypted_line + '\n')

def read_all():
    if not ENCRYPTION_LOGS_FILE.exists():
        return []
    
    records = []
    with open(ENCRYPTION_LOGS_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    decrypted = decrypt(line)
                    record = json.loads(decrypted)
                    records.append(record)
                except:
                    continue
    
    return records
