# src/infrastructure/adapters/user_repo_sqlite.py

from src.application.ports.user_repo import UserRepo
from src.infrastructure.db.user_repo_sqlite import get_by_username_norm, add, update_password

class UserRepoSqlite(UserRepo):
    def get_by_username_norm(self, username_norm: str):
        return get_by_username_norm(username_norm)
    
    def add(self, username_norm: str, pw_hash: str, role: str, first_name: str, last_name: str, registered_at: str) -> int:
        return add(username_norm, pw_hash, role, first_name, last_name, registered_at)
    
    def update_password(self, user_id: int, new_hash: str) -> None:
        return update_password(user_id, new_hash)
