

from src.application.ports.sec_logger import SecLogger
from src.infrastructure.logging.sec_logger import log, read_all

class SecLoggerEncrypted(SecLogger):
    def log(self, event: str, user: str = None, details: dict = None, suspicious: bool = False) -> None:
        return log(event, user, details, suspicious)
    
    def read_all(self):
        return read_all()
