# src/application/ports/scooter_repo.py

from abc import ABC, abstractmethod

class ScooterRepo(ABC):
    @abstractmethod
    def add(self, brand: str, model: str, serial_number: str, max_speed: int, 
            battery_capacity: int, soc: int, latitude: float, longitude: float, 
            in_service_date: str, status: str = "active") -> int:
        pass
    
    @abstractmethod
    def get_by_id(self, scooter_id: int):
        pass
    
    @abstractmethod
    def get_by_serial(self, serial_number: str):
        pass
    
    @abstractmethod
    def update(self, scooter_id: int, **kwargs) -> bool:
        pass
    
    @abstractmethod
    def search(self, search_term: str):
        pass
    
    @abstractmethod
    def all(self):
        pass
    
    @abstractmethod
    def delete(self, scooter_id: int) -> bool:
        pass
