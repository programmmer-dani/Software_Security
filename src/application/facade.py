

import secrets
from src.application.use_cases.auth import login as auth_login, change_password as auth_change_password
from src.application.security.acl import CurrentUser, require_super_admin, require_admin, require_engineer_or_admin
from src.domain.validators import validate_username, validate_password, validate_zip, validate_phone, validate_license, validate_gender, validate_city, validate_birthday, validate_soc, validate_latitude, validate_longitude
from src.domain.errors import ValidationError
from src.domain.constants import ROLES
from src.domain.models import User, Traveller, RestoreCode, Scooter
from src.domain.policies import can_create_sys_admin, can_create_backup, can_generate_restore_code, can_restore_any_backup, can_restore_with_code, can_consume_restore_code
from src.domain.services import generate_customer_id
from src.application.ports.user_repo import UserRepo
from src.application.ports.traveller_repo import TravellerRepo
from src.application.ports.scooter_repo import ScooterRepo
from src.application.ports.restore_code_repo import RestoreCodeRepo
from src.application.ports.log_state_repo import LogStateRepo
from src.application.ports.password_hasher import PasswordHasher
from src.application.ports.crypto_box import CryptoBox
from src.application.ports.sec_logger import SecLogger
from src.application.ports.backup_store import BackupStore

class App:
    def __init__(self, user_repo: UserRepo, traveller_repo: TravellerRepo, scooter_repo: ScooterRepo, 
                 restore_code_repo: RestoreCodeRepo, log_state_repo: LogStateRepo, password_hasher: PasswordHasher, 
                 crypto_box: CryptoBox, logger: SecLogger, backup_store: BackupStore):

        self.user_repo = user_repo
        self.traveller_repo = traveller_repo
        self.scooter_repo = scooter_repo
        self.restore_code_repo = restore_code_repo
        self.log_state_repo = log_state_repo
        self.password_hasher = password_hasher
        self.crypto_box = crypto_box
        self.logger = logger
        self.backup_store = backup_store

    def login(self, username: str, password: str) -> CurrentUser:
        return auth_login(self, username, password)
    
    def change_password(self, current_user: CurrentUser, old_password: str, new_password: str):
        return auth_change_password(self, current_user, old_password, new_password)
    
    def create_sys_admin(self, current_user: CurrentUser, username: str, password: str, first_name: str = "", last_name: str = ""):

        if not can_create_sys_admin(current_user.role):
            raise ValidationError("Access denied. Insufficient permissions.")

        validated_username = validate_username(username)
        validated_password = validate_password(password)

        username_norm = validated_username

        user = User.new_sys_admin(username_norm, first_name, last_name)

        pw_hash = self.password_hasher.hash(validated_password)

        self.user_repo.add(
            username_norm,
            pw_hash,
            user.role,
            user.first_name,
            user.last_name,
            user.registered_at
        )
    
    def add_traveller(self, current_user: CurrentUser, first_name: str, last_name: str, birthday: str, gender: str,
                     street: str, house_no: str, zip_code: str, city: str, email: str, phone: str, license_no: str):
        require_engineer_or_admin(current_user)

        first_name = _validate_input(first_name, "First name")
        last_name = _validate_input(last_name, "Last name")
        birthday = validate_birthday(birthday)
        gender = validate_gender(gender)
        street = _validate_input(street, "Street")
        house_no = _validate_input(house_no, "House number")
        zip_code = validate_zip(zip_code)
        city = validate_city(city)
        email = _validate_input(email, "Email")
        phone = validate_phone(phone)
        license_no = validate_license(license_no)

        random_suffix = secrets.randbelow(10000)
        customer_id = generate_customer_id(f"_{random_suffix:04d}")

        traveller = Traveller.new_with_customer_id(
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
            license=license_no
        )

        self.traveller_repo.add(
            traveller.customer_id,
            traveller.first_name,
            traveller.last_name,
            traveller.birthday,
            traveller.gender,
            traveller.street,
            traveller.house_no,
            traveller.zip_code,
            traveller.city,
            traveller.email,
            traveller.phone,
            traveller.license,
            traveller.registered_at
        )
        return traveller.customer_id
    
    def search_travellers(self, current_user: CurrentUser, search_term: str):
        require_engineer_or_admin(current_user)
        travellers = self.traveller_repo.all()
        
        matches = []
        for traveller in travellers:
            first_name = self.crypto_box.decrypt(traveller['first_name_enc'])
            last_name = self.crypto_box.decrypt(traveller['last_name_enc'])
            customer_id = traveller['customer_id']

            from src.domain.services import matches_partial
            if (matches_partial(first_name, search_term) or 
                matches_partial(last_name, search_term) or 
                matches_partial(customer_id, search_term)):
                matches.append(traveller)
        
        return matches
    
    def create_backup(self, current_user: CurrentUser):

        if not can_create_backup(current_user.role):
            raise ValidationError("Access denied. Insufficient permissions.")
        
        return self.backup_store.create_backup()
    
    def generate_restore_code(self, current_user: CurrentUser, backup_name: str, target_username: str):

        if not can_generate_restore_code(current_user.role):
            raise ValidationError("Access denied. Insufficient permissions.")

        username_norm = validate_username(target_username)

        target_user = self.user_repo.get_by_username_norm(username_norm)
        if not target_user:
            raise ValidationError("Target user not found")

        restore_code_model = RestoreCode.new(backup_name, target_user['id'])

        restore_code = secrets.token_urlsafe(32)
        code_hash = self.password_hasher.hash_token(restore_code)

        self.restore_code_repo.insert(backup_name, target_user['id'], code_hash)
        return restore_code
    
    def restore_any_backup(self, current_user: CurrentUser, backup_name: str):

        if not can_restore_any_backup(current_user.role):
            raise ValidationError("Access denied. Only Super Admin can restore backups directly.")

        self.backup_store.restore_from_backup(backup_name)
        return True
    
    def restore_with_code(self, current_user: CurrentUser, backup_name: str, restore_code: str):

        if not can_restore_with_code(current_user.role):
            raise ValidationError("Access denied. Only System Admin can restore with restore codes.")

        if not can_consume_restore_code(current_user.role):
            raise ValidationError("Access denied. Super Admin cannot consume restore codes.")
        
        success = self.restore_code_repo.consume(current_user.id, backup_name, restore_code)
        
        if success:
            self.backup_store.restore_from_backup(backup_name)
            return True
        else:
            return False
    
    def view_logs(self, current_user: CurrentUser):
        require_admin(current_user)
        return self.logger.read_all()
    
    def get_unread_suspicious_count(self, current_user: CurrentUser) -> int:
        require_admin(current_user)
        return self.log_state_repo.get_unread_suspicious_count(current_user.id)
    
    def mark_all_seen(self, current_user: CurrentUser):
        require_admin(current_user)
        return self.log_state_repo.mark_all_seen(current_user.id)

    def add_scooter(self, current_user: CurrentUser, brand: str, model: str, serial_number: str, 
                    top_speed: int, battery_capacity: int, soc: int, target_soc_min: int, target_soc_max: int,
                    latitude: float, longitude: float, out_of_service: bool, mileage: int,
                    last_maintenance_date: str, in_service_date: str, status: str = "active"):
        require_admin(current_user)

        brand = _validate_input(brand, "Brand")
        model = _validate_input(model, "Model")
        serial_number = _validate_input(serial_number, "Serial number")
        top_speed = int(top_speed)
        battery_capacity = int(battery_capacity)
        soc = validate_soc(soc)
        target_soc_min = int(target_soc_min)
        target_soc_max = int(target_soc_max)
        latitude = validate_latitude(latitude)
        longitude = validate_longitude(longitude)
        mileage = int(mileage)
        last_maintenance_date = _validate_input(last_maintenance_date, "Last maintenance date")
        in_service_date = _validate_input(in_service_date, "In service date")
        status = _validate_input(status, "Status")

        existing = self.scooter_repo.get_by_serial(serial_number)
        if existing:
            raise ValidationError("Scooter with this serial number already exists")

        scooter_id = self.scooter_repo.add(
            brand=brand,
            model=model,
            serial_number=serial_number,
            top_speed=top_speed,
            battery_capacity=battery_capacity,
            soc=soc,
            target_soc_min=target_soc_min,
            target_soc_max=target_soc_max,
            latitude=latitude,
            longitude=longitude,
            out_of_service=out_of_service,
            mileage=mileage,
            last_maintenance_date=last_maintenance_date,
            in_service_date=in_service_date,
            status=status
        )

        self.logger.log('scooter_created', current_user.username_norm, 
                       {'scooter_id': scooter_id, 'serial_number': serial_number}, False)
        
        return scooter_id
    
    def search_scooters(self, current_user: CurrentUser, search_term: str):
        require_engineer_or_admin(current_user)
        return self.scooter_repo.search(search_term)
    
    def update_scooter(self, current_user: CurrentUser, scooter_id: int, **kwargs):
        require_engineer_or_admin(current_user)

        scooter = self.scooter_repo.get_by_id(scooter_id)
        if not scooter:
            raise ValidationError("Scooter not found")

        if 'soc' in kwargs:
            kwargs['soc'] = validate_soc(kwargs['soc'])
        if 'latitude' in kwargs:
            kwargs['latitude'] = validate_latitude(kwargs['latitude'])
        if 'longitude' in kwargs:
            kwargs['longitude'] = validate_longitude(kwargs['longitude'])
        if 'max_speed' in kwargs:
            kwargs['max_speed'] = int(kwargs['max_speed'])
        if 'battery_capacity' in kwargs:
            kwargs['battery_capacity'] = int(kwargs['battery_capacity'])

        success = self.scooter_repo.update(scooter_id, **kwargs)
        
        if success:

            self.logger.log('scooter_updated', current_user.username_norm, 
                           {'scooter_id': scooter_id, 'updates': list(kwargs.keys())}, False)
        
        return success
    
    def get_scooter(self, current_user: CurrentUser, scooter_id: int):
        require_engineer_or_admin(current_user)
        return self.scooter_repo.get_by_id(scooter_id)
    
    def delete_scooter(self, current_user: CurrentUser, scooter_id: int):
        require_admin(current_user)

        scooter = self.scooter_repo.get_by_id(scooter_id)
        if not scooter:
            raise ValidationError("Scooter not found")

        success = self.scooter_repo.delete(scooter_id)
        
        if success:

            self.logger.log('scooter_deleted', current_user.username_norm, 
                           {'scooter_id': scooter_id, 'serial_number': scooter['serial_number']}, False)
        
        return success

    def create_service_engineer(self, current_user: CurrentUser, username: str, password: str, 
                               first_name: str = "", last_name: str = ""):
        require_admin(current_user)

        validated_username = validate_username(username)
        validated_password = validate_password(password)

        user = User.new_service_engineer(validated_username, first_name, last_name)

        pw_hash = self.password_hasher.hash(validated_password)

        self.user_repo.add(
            validated_username,
            pw_hash,
            user.role,
            user.first_name,
            user.last_name,
            user.registered_at
        )

        self.logger.log('service_engineer_created', current_user.username_norm, 
                       {'created_username': validated_username}, False)
    
    def update_service_engineer(self, current_user: CurrentUser, engineer_username: str, 
                              first_name: str = None, last_name: str = None):
        require_admin(current_user)

        validated_username = validate_username(engineer_username)

        engineer = self.user_repo.get_by_username_norm(validated_username)
        if not engineer:
            raise ValidationError("Service Engineer not found")
        
        if engineer['role'] != ROLES[2]:
            raise ValidationError("User is not a Service Engineer")

        updates = {}
        if first_name is not None:
            updates['first_name'] = _validate_input(first_name, "First name")
        if last_name is not None:
            updates['last_name'] = _validate_input(last_name, "Last name")
        
        if not updates:
            raise ValidationError("No updates provided")

        self.logger.log('service_engineer_updated', current_user.username_norm, 
                       {'engineer_username': validated_username, 'updates': list(updates.keys())}, False)
    
    def delete_service_engineer(self, current_user: CurrentUser, engineer_username: str):
        require_admin(current_user)

        validated_username = validate_username(engineer_username)

        engineer = self.user_repo.get_by_username_norm(validated_username)
        if not engineer:
            raise ValidationError("Service Engineer not found")
        
        if engineer['role'] != ROLES[2]:
            raise ValidationError("User is not a Service Engineer")

        self.logger.log('service_engineer_deleted', current_user.username_norm, 
                       {'deleted_username': validated_username}, False)
    
    def reset_service_engineer_password(self, current_user: CurrentUser, engineer_username: str, 
                                       new_password: str):
        require_admin(current_user)

        validated_username = validate_username(engineer_username)

        engineer = self.user_repo.get_by_username_norm(validated_username)
        if not engineer:
            raise ValidationError("Service Engineer not found")
        
        if engineer['role'] != ROLES[2]:
            raise ValidationError("User is not a Service Engineer")

        validated_password = validate_password(new_password)

        new_hash = self.password_hasher.hash(validated_password)

        self.user_repo.update_password(engineer['id'], new_hash)

        self.logger.log('service_engineer_password_reset', current_user.username_norm, 
                       {'engineer_username': validated_username}, False)

def _validate_input(value: str, field: str) -> str:
    if value is None:
        raise ValidationError(f"{field} cannot be empty")
    
    value = str(value)
    if not value:
        raise ValidationError(f"{field} cannot be empty")
    
    if len(value) > 1000:
        raise ValidationError(f"{field} is too long")
    
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise ValidationError(f"{field} contains invalid characters")
    
    return value
