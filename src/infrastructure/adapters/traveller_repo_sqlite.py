

from src.application.ports.traveller_repo import TravellerRepo
from src.infrastructure.db.traveller_repo_sqlite import add, all, get_by_id, update, delete

class TravellerRepoSqlite(TravellerRepo):
    def add(self, customer_id: str, first_name: str, last_name: str, birthday: str, gender: str,
            street: str, house_no: str, zip_code: str, city: str, email: str, phone: str, license: str, registered_at: str) -> int:
        return add(customer_id, first_name, last_name, birthday, gender, street, house_no, zip_code, city, email, phone, license, registered_at)
    
    def all(self):
        return all()
    
    def get_by_id(self, traveller_id: int):
        return get_by_id(traveller_id)
    
    def update(self, traveller_id: int, **kwargs) -> bool:
        return update(traveller_id, **kwargs)
    
    def delete(self, traveller_id: int) -> bool:
        return delete(traveller_id)
