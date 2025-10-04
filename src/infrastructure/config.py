# src/infrastructure/config.py

from pathlib import Path

# File paths
DATA_DIR = Path("data")
DATABASE_FILE = DATA_DIR / "app.db"
ENCRYPTION_KEY_FILE = DATA_DIR / "keys" / "app.key"
ENCRYPTION_LOGS_FILE = DATA_DIR / "logs.enc"
BACKUP_FOLDER = DATA_DIR / "backups"

# System constants (business constants moved to domain/constants.py)

def ensure_directories_exist():
    for directory in [DATA_DIR, DATA_DIR / "keys", DATA_DIR / "backups"]:
        directory.mkdir(parents=True, exist_ok=True)

ensure_directories_exist()