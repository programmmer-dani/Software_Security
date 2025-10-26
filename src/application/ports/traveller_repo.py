

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class TravellerRepo(ABC):
    @abstractmethod
    def add(self, customer_id: str, first_name: str, last_name: str, birthday: str, gender: str,
            street: str, house_no: str, zip_code: str, city: str, email: str, phone: str, license: str, registered_at: str) -> int:
        pass
    
    @abstractmethod
    def all(self) -> List[Dict[str, Any]]:
        pass
