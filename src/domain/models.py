# src/domain/models.py

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
            role=ROLES[1],  # SYS_ADMIN
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
    max_speed: int
    battery_capacity: int
    soc: int
    latitude: float
    longitude: float
    in_service_date: str
    status: str
    
    @classmethod
    def new(cls, brand: str, model: str, serial_number: str, max_speed: int, 
            battery_capacity: int, soc: int, latitude: float, longitude: float, 
            in_service_date: str, status: str = "active"):
        return cls(
            id=None,
            brand=brand,
            model=model,
            serial_number=serial_number,
            max_speed=max_speed,
            battery_capacity=battery_capacity,
            soc=soc,
            latitude=latitude,
            longitude=longitude,
            in_service_date=in_service_date,
            status=status
        )

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
