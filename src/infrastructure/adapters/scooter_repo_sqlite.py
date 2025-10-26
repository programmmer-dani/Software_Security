

from src.application.ports.scooter_repo import ScooterRepo
from src.infrastructure.db.scooter_repo_sqlite import (
    add, get_by_id, get_by_serial, update, search, all, delete
)

class ScooterRepoSqlite(ScooterRepo):
    def add(self, brand: str, model: str, serial_number: str, top_speed: int, 
            battery_capacity: int, soc: int, target_soc_min: int, target_soc_max: int,
            latitude: float, longitude: float, out_of_service: bool, mileage: int,
            last_maintenance_date: str, in_service_date: str, status: str = "active") -> int:
        return add(brand, model, serial_number, top_speed, battery_capacity, 
                  soc, target_soc_min, target_soc_max, latitude, longitude, 
                  out_of_service, mileage, last_maintenance_date, in_service_date, status)
    
    def get_by_id(self, scooter_id: int):
        return get_by_id(scooter_id)
    
    def get_by_serial(self, serial_number: str):
        return get_by_serial(serial_number)
    
    def update(self, scooter_id: int, **kwargs) -> bool:
        return update(scooter_id, **kwargs)
    
    def search(self, search_term: str):
        return search(search_term)
    
    def all(self):
        return all()
    
    def delete(self, scooter_id: int) -> bool:
        return delete(scooter_id)
