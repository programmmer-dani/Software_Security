

from src.application.ports.restore_code_repo import RestoreCodeRepo
from src.infrastructure.db.restore_code_repo_sqlite import insert, consume

class RestoreCodeRepoSqlite(RestoreCodeRepo):
    def insert(self, backup_name: str, user_id: int, code_hash: str) -> int:
        return insert(backup_name, user_id, code_hash)
    
    def consume(self, user_id: int, backup_name: str, candidate_code: str) -> bool:
        return consume(user_id, backup_name, candidate_code)
