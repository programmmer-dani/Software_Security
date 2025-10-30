

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class TravellerRepo(ABC):
    @abstractmethod
    def add(self, customer_id: str, first_name: str, last_name: str, birthday: str, gender: str,
            street: str, house_no: str, zip_code: str, city: str, email: str, phone: str, license: str, registered_at: str) -> int:
        pass
    
    @abstractmethod
    def all(self) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_by_id(self, traveller_id: int) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def update(self, traveller_id: int, **kwargs) -> bool:
        pass
    
    @abstractmethod
    def delete(self, traveller_id: int) -> bool:
        pass