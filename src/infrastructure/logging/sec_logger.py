

import json
from datetime import datetime
from src.infrastructure.config import ENCRYPTION_LOGS_FILE
from src.infrastructure.crypto.fernet_box import encrypt, decrypt

def _get_next_rowid():

    existing_logs = read_all()
    if not existing_logs:
        return 1
    
    max_rowid = max(log.get('rowid', 0) for log in existing_logs)
    return max_rowid + 1

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
