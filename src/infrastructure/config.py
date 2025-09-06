# src/infrastructure/config.py
"""
Centralized configuration file for all file paths and system constants.
This module ensures all paths and constants are defined in one place
and creates necessary directories automatically.
"""

import os
from pathlib import Path
from typing import Tuple, List

# =============================================================================
# FILE PATHS
# =============================================================================

# Base data directory
DATA_DIR = Path("data")

# Main file paths
DATABASE_FILE = DATA_DIR / "app.db"
ENCRYPTION_KEY_FILE = DATA_DIR / "keys" / "app.key"
ENCRYPTED_LOGS_FILE = DATA_DIR / "logs.enc"
BACKUP_FOLDER = DATA_DIR / "backups"

# =============================================================================
# SYSTEM CONSTANTS
# =============================================================================

# Valid user roles
USER_ROLES: Tuple[str, ...] = ("SUPER_ADMIN", "SYS_ADMIN", "ENGINEER")

# List of 10 cities for traveller validation
CITIES: List[str] = [
    "Amsterdam",
    "Rotterdam", 
    "The Hague",
    "Utrecht",
    "Eindhoven",
    "Tilburg",
    "Groningen",
    "Almere",
    "Breda",
    "Nijmegen"
]

# Rotterdam coordinates for scooter location validation
# Latitude and longitude bounding box for Rotterdam area
ROTTERDAM_LAT_MIN = 51.85
ROTTERDAM_LAT_MAX = 51.95
ROTTERDAM_LON_MIN = 4.35
ROTTERDAM_LON_MAX = 4.55

# =============================================================================
# DIRECTORY CREATION
# =============================================================================

def ensure_directories_exist() -> None:
    """
    Ensure all required directories exist.
    Creates directories if they don't exist.
    """
    directories_to_create = [
        DATA_DIR,
        DATA_DIR / "keys",
        DATA_DIR / "backups"
    ]
    
    for directory in directories_to_create:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directory ensured: {directory}")

# =============================================================================
# INITIALIZATION
# =============================================================================

# Automatically create directories when this module is imported
if __name__ == "__main__":
    print("Creating required directories...")
    ensure_directories_exist()
    print("Configuration loaded successfully!")
else:
    # Only print when imported, not when run directly
    ensure_directories_exist()
