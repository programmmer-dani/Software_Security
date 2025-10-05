# src/application/facade.py

import secrets
from datetime import datetime
from src.application.use_cases.auth import login as auth_login, change_password as auth_change_password
from src.application.security.acl import CurrentUser, require_super_admin, require_admin, require_engineer_or_admin
from src.domain.validators import validate_username, validate_password, validate_zip, validate_phone, validate_license, validate_gender, validate_city, validate_birthday
from src.domain.errors import ValidationError
from src.domain.constants import ROLES
from src.domain.models import User, Traveller, RestoreCode
from src.domain.policies import can_create_sys_admin, can_create_backup, can_generate_restore_code, can_restore_any_backup, can_restore_with_code, can_consume_restore_code
from src.domain.services import generate_customer_id
from src.application.ports.user_repo import UserRepo
from src.application.ports.traveller_repo import TravellerRepo
from src.application.ports.restore_code_repo import RestoreCodeRepo
from src.application.ports.log_state_repo import LogStateRepo
from src.application.ports.password_hasher import PasswordHasher
from src.application.ports.crypto_box import CryptoBox
from src.application.ports.sec_logger import SecLogger
from src.application.ports.backup_store import BackupStore

class App:
    def __init__(self, user_repo: UserRepo, traveller_repo: TravellerRepo, restore_code_repo: RestoreCodeRepo, 
                 log_state_repo: LogStateRepo, password_hasher: PasswordHasher, crypto_box: CryptoBox, 
                 logger: SecLogger, backup_store: BackupStore):
        # Inject dependencies via ports
        self.user_repo = user_repo
        self.traveller_repo = traveller_repo
        self.restore_code_repo = restore_code_repo
        self.log_state_repo = log_state_repo
        self.password_hasher = password_hasher
        self.crypto_box = crypto_box
        self.logger = logger
        self.backup_store = backup_store
    
    # Application methods for CLI
    def login(self, username: str, password: str) -> CurrentUser:
        return auth_login(self, username, password)
    
    def change_password(self, current_user: CurrentUser, old_password: str, new_password: str):
        return auth_change_password(self, current_user, old_password, new_password)
    
    def create_sys_admin(self, current_user: CurrentUser, username: str, password: str, first_name: str = "", last_name: str = ""):
        # Check policy for authorization
        if not can_create_sys_admin(current_user.role):
            raise ValidationError("Access denied. Insufficient permissions.")
        
        # Validate inputs
        validate_username(username)
        validate_password(password)
        
        # Use validated username as-is
        username_norm = username
        
        # Create domain model
        user = User.new_sys_admin(username_norm, first_name, last_name)
        
        # Hash password (outside domain)
        pw_hash = self.password_hasher.hash(validated_password)
        
        # Persist via repository
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
        
        # Validate inputs
        first_name = _clean_input(first_name, "First name")
        last_name = _clean_input(last_name, "Last name")
        birthday = validate_birthday(birthday)
        gender = validate_gender(gender)
        street = _clean_input(street, "Street")
        house_no = _clean_input(house_no, "House number")
        zip_code = validate_zip(zip_code)
        city = validate_city(city)
        email = _clean_input(email, "Email")
        phone = validate_phone(phone)
        license_no = validate_license(license_no)
        
        # Generate customer ID using domain service
        import secrets
        random_suffix = secrets.randbelow(10000)  # 4-digit random number
        customer_id = generate_customer_id(f"_{random_suffix:04d}")
        
        # Create domain model
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
        
        # Persist via repository (encryption happens in repo)
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
            
            # Use domain service for case-insensitive search
            from src.domain.services import matches_partial
            if (matches_partial(first_name, search_term) or 
                matches_partial(last_name, search_term) or 
                matches_partial(customer_id, search_term)):
                matches.append(traveller)
        
        return matches
    
    def create_backup(self, current_user: CurrentUser):
        # Check policy for authorization
        if not can_create_backup(current_user.role):
            raise ValidationError("Access denied. Insufficient permissions.")
        
        return self.backup_store.create_backup()
    
    def generate_restore_code(self, current_user: CurrentUser, backup_name: str, target_username: str):
        # Check policy for authorization
        if not can_generate_restore_code(current_user.role):
            raise ValidationError("Access denied. Insufficient permissions.")
        
        # Validate inputs
        validate_username(target_username)
        
        # Use validated username as-is
        username_norm = target_username
        
        # Get target user
        target_user = self.user_repo.get_by_username_norm(username_norm)
        if not target_user:
            raise ValidationError("Target user not found")
        
        # Create domain model
        restore_code_model = RestoreCode.new(backup_name, target_user['id'])
        
        # Generate restore code and hash it (outside domain)
        restore_code = secrets.token_urlsafe(32)
        code_hash = self.password_hasher.hash_token(restore_code)
        
        # Persist via repository
        self.restore_code_repo.insert(backup_name, target_user['id'], code_hash)
        return restore_code
    
    def restore_any_backup(self, current_user: CurrentUser, backup_name: str):
        """Restore any backup directly (SUPER_ADMIN only, no restore code needed)."""
        # Check policy for authorization
        if not can_restore_any_backup(current_user.role):
            raise ValidationError("Access denied. Only Super Admin can restore backups directly.")
        
        # Direct restore without restore code
        self.backup_store.restore_from_backup(backup_name)
        return True
    
    def restore_with_code(self, current_user: CurrentUser, backup_name: str, restore_code: str):
        """Restore backup using a restore code (SYS_ADMIN only)."""
        # Check policy for authorization
        if not can_restore_with_code(current_user.role):
            raise ValidationError("Access denied. Only System Admin can restore with restore codes.")
        
        # Check if user can consume restore codes
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

def _clean_input(value: str, field: str) -> str:
    if value is None:
        raise ValidationError(f"{field} cannot be empty")
    
    value = str(value)
    if not value:
        raise ValidationError(f"{field} cannot be empty")
    
    if len(value) > 1000:
        raise ValidationError(f"{field} is too long")
    
    if '\x00' in value:
        raise ValidationError(f"{field} contains invalid characters")
    
    return value
