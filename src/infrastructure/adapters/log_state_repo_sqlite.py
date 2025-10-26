

from src.application.ports.log_state_repo import LogStateRepo
from src.infrastructure.db.log_state_repo_sqlite import get_unread_suspicious_count, mark_all_seen

class LogStateRepoSqlite(LogStateRepo):
    def get_unread_suspicious_count(self, user_id: int) -> int:
        return get_unread_suspicious_count(user_id)
    
    def mark_all_seen(self, user_id: int) -> None:
        return mark_all_seen(user_id)
