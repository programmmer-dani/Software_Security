

import sys
import os

if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.infrastructure.db.sqlite import migrate
from src.application.facade import App
from src.presentation import cli
from src.infrastructure.adapters.user_repo_sqlite import UserRepoSqlite
from src.infrastructure.adapters.traveller_repo_sqlite import TravellerRepoSqlite
from src.infrastructure.adapters.scooter_repo_sqlite import ScooterRepoSqlite
from src.infrastructure.adapters.restore_code_repo_sqlite import RestoreCodeRepoSqlite
from src.infrastructure.adapters.log_state_repo_sqlite import LogStateRepoSqlite
from src.infrastructure.adapters.password_hasher_argon2 import PasswordHasherArgon2
from src.infrastructure.adapters.crypto_box_fernet import CryptoBoxFernet
from src.infrastructure.adapters.sec_logger_encrypted import SecLoggerEncrypted
from src.infrastructure.adapters.backup_store_zip import BackupStoreZip

def main():
    print("App starting…")

    migrate()

    user_repo = UserRepoSqlite()
    traveller_repo = TravellerRepoSqlite()
    scooter_repo = ScooterRepoSqlite()
    restore_code_repo = RestoreCodeRepoSqlite()
    log_state_repo = LogStateRepoSqlite()
    password_hasher = PasswordHasherArgon2()
    crypto_box = CryptoBoxFernet()
    logger = SecLoggerEncrypted()
    backup_store = BackupStoreZip()

    app = App(user_repo, traveller_repo, scooter_repo, restore_code_repo, log_state_repo, 
              password_hasher, crypto_box, logger, backup_store)

    cli.run(app)

if __name__ == "__main__":
    main()
