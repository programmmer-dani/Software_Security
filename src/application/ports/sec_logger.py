# src/application/ports/sec_logger.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class SecLogger(ABC):
    @abstractmethod
    def log(self, event: str, user: str = None, details: dict = None, suspicious: bool = False) -> None:
        pass
    
    @abstractmethod
    def read_all(self) -> List[Dict[str, Any]]:
        pass
