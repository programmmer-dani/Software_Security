

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from .constants import ROLES

@dataclass
class User:
    id: Optional[int]
    username_norm: str
    role: str
    first_name: Optional[str]
    last_name: Optional[str]
    registered_at: str
    
    @classmethod
    def new_sys_admin(cls, username_norm: str, first_name: str = "", last_name: str = "", registered_at: str = None):
        if registered_at is None:
            registered_at = datetime.now().isoformat()
        return cls(
            id=None,
            username_norm=username_norm,
            role=ROLES[1],
            first_name=first_name,
            last_name=last_name,
            registered_at=registered_at
        )
    
    @classmethod
    def new_service_engineer(cls, username_norm: str, first_name: str = "", last_name: str = "", registered_at: str = None):
        if registered_at is None:
            registered_at = datetime.now().isoformat()
        return cls(
            id=None,
            username_norm=username_norm,
            role=ROLES[2],
            first_name=first_name,
            last_name=last_name,
            registered_at=registered_at
        )

@dataclass
class Traveller:
    id: Optional[int]
    customer_id: str
    first_name: str
    last_name: str
    birthday: str
    gender: str
    street: str
    house_no: str
    zip_code: str
    city: str
    email: str
    phone: str
    license: str
    registered_at: str
    
    @classmethod
    def new_with_customer_id(cls, customer_id: str, first_name: str, last_name: str, birthday: str, 
                           gender: str, street: str, house_no: str, zip_code: str, city: str, 
                           email: str, phone: str, license: str, registered_at: str = None):
        if not customer_id:
            raise ValueError("Customer ID is required")
        if registered_at is None:
            registered_at = datetime.now().isoformat()
        return cls(
            id=None,
            customer_id=customer_id,
            first_name=first_name,
            last_name=last_name,
            birthday=birthday,
            gender=gender,
            street=street,
            house_no=house_no,
            zip_code=zip_code,
            city=city,
            email=email,
            phone=phone,
            license=license,
            registered_at=registered_at
        )

@dataclass
class Scooter:
    id: Optional[int]
    brand: str
    model: str
    serial_number: str
    top_speed: int
    battery_capacity: int
    soc: int
    target_soc_min: int
    target_soc_max: int
    latitude: float
    longitude: float
    out_of_service: bool
    mileage: int
    last_maintenance_date: str
    in_service_date: str
    status: str

@dataclass
class RestoreCode:
    id: Optional[int]
    backup_name: str
    granted_to_user_id: int
    used: bool
    created_at: str
    
    @classmethod
    def new(cls, backup_name: str, granted_to_user_id: int, created_at: str = None):
        if created_at is None:
            created_at = datetime.now().isoformat()
        return cls(
            id=None,
            backup_name=backup_name,
            granted_to_user_id=granted_to_user_id,
            used=False,
            created_at=created_at
        )
