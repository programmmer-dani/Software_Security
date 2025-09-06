# src/infrastructure/config.py

from pathlib import Path

# File paths
DATA_DIR = Path("data")
DATABASE_FILE = DATA_DIR / "app.db"
ENCRYPTION_KEY_FILE = DATA_DIR / "keys" / "app.key"
ENCRYPTION_LOGS_FILE = DATA_DIR / "logs.enc"
BACKUP_FOLDER = DATA_DIR / "backups"

# System constants
USER_ROLES = ("SUPER_ADMIN", "SYS_ADMIN", "ENGINEER")

CITIES = [
    "Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven",
    "Tilburg", "Groningen", "Almere", "Breda", "Nijmegen"
]

# Rotterdam bounds
ROTTERDAM_LAT_MIN = 51.85
ROTTERDAM_LAT_MAX = 51.95
ROTTERDAM_LON_MIN = 4.35
ROTTERDAM_LON_MAX = 4.55

def ensure_directories_exist():
    for directory in [DATA_DIR, DATA_DIR / "keys", DATA_DIR / "backups"]:
        directory.mkdir(parents=True, exist_ok=True)

ensure_directories_exist()