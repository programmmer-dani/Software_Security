import sys
from datetime import datetime
from typing import Optional

from src.application.security.acl import CurrentUser
from src.application.use_cases.auth import login, change_password
from src.domain.errors import ValidationError
from src.domain.validators import (
    validate_username, validate_password, validate_zip, validate_phone,
    validate_license, validate_gender, validate_city, validate_birthday
)
from src.infrastructure.db.sqlite import migrate
from src.infrastructure.db.user_repo_sqlite import add as add_user, get_by_username_norm
from src.infrastructure.db.traveller_repo_sqlite import add as add_traveller, all as get_all_travellers
from src.infrastructure.db.restore_code_repo_sqlite import insert as insert_restore_code, consume as consume_restore_code
from src.infrastructure.db.log_state_repo_sqlite import get_unread_suspicious_count, mark_all_seen
from src.infrastructure.logging.sec_logger import read_all
from src.infrastructure.backup.zip_store import create_backup, restore_from_backup


def run():
    """Main application entry point."""
    migrate()
    
    current_user: Optional[CurrentUser] = None
    
    while True:
        if current_user is None:
            current_user = main_menu()
        else:
            current_user = role_menu(current_user)


def main_menu() -> Optional[CurrentUser]:
    """Main menu for unauthenticated users."""
    while True:
        print("\n" + "="*50)
        print("UM Members Management System")
        print("="*50)
        print("1) Login")
        print("2) Exit")
        
        choice = input("\nChoose option (1-2): ").strip()
        
        if choice == "1":
            return login_flow()
        elif choice == "2":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid option. Please choose 1 or 2.")


def login_flow() -> Optional[CurrentUser]:
    """Handle user login."""
    print("\n" + "-"*30)
    print("LOGIN")
    print("-"*30)
    
    try:
        username = input("Username: ").strip()
        if not username:
            print("Username cannot be empty.")
            return None
            
        password = input("Password: ").strip()
        if not password:
            print("Password cannot be empty.")
            return None
        
        try:
            username = validate_username(username)
        except ValidationError as e:
            print(f"Invalid username: {e}")
            return None
        
        user = login(username, password)
        
        if user:
            print(f"\nWelcome, {user.role}!")
            
            if user.role in ["SUPER_ADMIN", "SYS_ADMIN"]:
                unread_count = get_unread_suspicious_count(user.id)
                if unread_count > 0:
                    print(f"⚠ You have {unread_count} unread suspicious events.")
            
            return user
        else:
            print("Invalid credentials or account locked. Please try again later.")
            return None
            
    except ValidationError as e:
        print(f"Error: {e}")
        return None
    except Exception as e:
        print("An error occurred. Please try again.")
        return None


def role_menu(current_user: CurrentUser) -> Optional[CurrentUser]:
    """Role-based menu system."""
    if current_user.role == "SUPER_ADMIN":
        return super_admin_menu(current_user)
    elif current_user.role == "SYS_ADMIN":
        return sys_admin_menu(current_user)
    else:
        print("Access denied. Unknown role.")
        return None


def super_admin_menu(current_user: CurrentUser) -> Optional[CurrentUser]:
    """Super Admin menu."""
    while True:
        print("\n" + "="*50)
        print("SUPER ADMIN MENU")
        print("="*50)
        print("A) Create System Admin")
        print("B) Generate Restore Code")
        print("C) Create Backup")
        print("D) View Logs")
        print("E) Logout")
        
        choice = input("\nChoose option (A-E): ").strip().upper()
        
        if choice == "A":
            create_system_admin()
        elif choice == "B":
            generate_restore_code()
        elif choice == "C":
            create_backup_flow()
        elif choice == "D":
            view_logs(current_user)
        elif choice == "E":
            return None
        else:
            print("Invalid option. Please choose A-E.")


def sys_admin_menu(current_user: CurrentUser) -> Optional[CurrentUser]:
    """System Admin menu."""
    while True:
        print("\n" + "="*50)
        print("SYSTEM ADMIN MENU")
        print("="*50)
        print("A) Change My Password")
        print("B) Add Traveller")
        print("C) Search Traveller")
        print("D) Restore from Backup")
        print("E) Create Backup")
        print("F) View Logs")
        print("G) Logout")
        
        choice = input("\nChoose option (A-G): ").strip().upper()
        
        if choice == "A":
            change_password_flow(current_user)
        elif choice == "B":
            add_traveller_flow()
        elif choice == "C":
            search_traveller_flow()
        elif choice == "D":
            restore_from_backup_flow()
        elif choice == "E":
            create_backup_flow()
        elif choice == "F":
            view_logs(current_user)
        elif choice == "G":
            return None
        else:
            print("Invalid option. Please choose A-G.")


def create_system_admin():
    """Create a new System Admin user."""
    print("\n" + "-"*30)
    print("CREATE SYSTEM ADMIN")
    print("-"*30)
    
    try:
        username = input("Username: ").strip()
        if not username:
            print("Username cannot be empty.")
            return
        
        password = input("Password: ").strip()
        if not password:
            print("Password cannot be empty.")
            return
        
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()
        
        username = validate_username(username)
        validate_password(password)
        
        from src.infrastructure.crypto.fernet_box import encrypt
        from src.infrastructure.crypto.argon2_hasher import hash
        
        user_data = {
            'username_norm': username,
            'username_enc': encrypt(username),
            'pw_hash': hash(password),
            'role': 'SYS_ADMIN',
            'first_name_enc': encrypt(first_name) if first_name else encrypt(""),
            'last_name_enc': encrypt(last_name) if last_name else encrypt(""),
            'registered_at': datetime.now().isoformat()
        }
        
        add_user(user_data)
        print("System Admin created successfully!")
        
    except ValidationError as e:
        print(f"Error: {e}")
    except Exception as e:
        print("Failed to create System Admin. Please try again.")


def change_password_flow(current_user: CurrentUser):
    """Handle password change."""
    print("\n" + "-"*30)
    print("CHANGE PASSWORD")
    print("-"*30)
    
    try:
        old_password = input("Current password: ").strip()
        if not old_password:
            print("Current password cannot be empty.")
            return
        
        new_password = input("New password: ").strip()
        if not new_password:
            print("New password cannot be empty.")
            return
        
        change_password(current_user, old_password, new_password)
        print("Password changed successfully!")
        
    except ValidationError as e:
        print(f"Error: {e}")
    except Exception as e:
        print("Failed to change password. Please try again.")


def add_traveller_flow():
    """Add a new traveller."""
    print("\n" + "-"*30)
    print("ADD TRAVELLER")
    print("-"*30)
    
    try:
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()
        birthday = input("Birthday (YYYY-MM-DD): ").strip()
        gender = input("Gender (male/female): ").strip()
        street = input("Street: ").strip()
        house_no = input("House number: ").strip()
        zip_code = input("ZIP code (DDDDXX): ").strip()
        city = input("City: ").strip()
        email = input("Email: ").strip()
        phone = input("Phone (8 digits): ").strip()
        license_no = input("Driving license: ").strip()
        
        validate_birthday(birthday)
        gender = validate_gender(gender)
        zip_code = validate_zip(zip_code)
        city = validate_city(city)
        phone = validate_phone(phone)
        license_no = validate_license(license_no)
        
        from src.infrastructure.crypto.fernet_box import encrypt
        customer_id = f"CUST_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        traveller_data = {
            'customer_id': customer_id,
            'first_name_enc': encrypt(first_name),
            'last_name_enc': encrypt(last_name),
            'birthday': birthday,
            'gender': gender,
            'street_enc': encrypt(street),
            'house_no_enc': encrypt(house_no),
            'zip_enc': encrypt(zip_code),
            'city': city,
            'email_enc': encrypt(email),
            'phone_enc': encrypt(phone),
            'license_enc': encrypt(license_no),
            'registered_at': datetime.now().isoformat()
        }
        
        add_traveller(traveller_data)
        print(f"Traveller added successfully! Customer ID: {customer_id}")
        
    except ValidationError as e:
        print(f"Error: {e}")
    except Exception as e:
        print("Failed to add traveller. Please try again.")


def search_traveller_flow():
    """Search for travellers."""
    print("\n" + "-"*30)
    print("SEARCH TRAVELLER")
    print("-"*30)
    print("Enter partial search term (name, customer ID, etc.)")
    
    search_term = input("Search: ").strip()
    if not search_term:
        print("Search term cannot be empty.")
        return
    
    try:
        travellers = get_all_travellers()
        from src.infrastructure.crypto.fernet_box import decrypt
        
        matches = []
        for traveller in travellers:
            first_name = decrypt(traveller['first_name_enc'])
            last_name = decrypt(traveller['last_name_enc'])
            customer_id = traveller['customer_id']
            
            if (search_term.lower() in first_name.lower() or 
                search_term.lower() in last_name.lower() or 
                search_term.lower() in customer_id.lower()):
                matches.append(traveller)
        
        if matches:
            print(f"\nFound {len(matches)} traveller(s):")
            print("-" * 60)
            for traveller in matches:
                first_name = decrypt(traveller['first_name_enc'])
                last_name = decrypt(traveller['last_name_enc'])
                print(f"ID: {traveller['id']} | Customer: {traveller['customer_id']} | Name: {first_name} {last_name}")
        else:
            print("No travellers found matching your search.")
            
    except Exception as e:
        print("Failed to search travellers. Please try again.")


def create_backup_flow():
    """Create a backup."""
    print("\n" + "-"*30)
    print("CREATE BACKUP")
    print("-"*30)
    
    try:
        backup_name = create_backup()
        print(f"Backup created: {backup_name}")
        
    except Exception as e:
        print(f"Failed to create backup: {e}")
        print("Please try again.")


def generate_restore_code():
    """Generate a restore code for Super Admin."""
    print("\n" + "-"*30)
    print("GENERATE RESTORE CODE")
    print("-"*30)
    
    try:
        backup_name = input("Backup name: ").strip()
        if not backup_name:
            print("Backup name cannot be empty.")
            return
        
        target_username = input("Target SysAdmin username: ").strip()
        if not target_username:
            print("Username cannot be empty.")
            return
        
        target_username = validate_username(target_username)
        
        target_user = get_by_username_norm(target_username)
        if not target_user:
            print("Target user not found.")
            return
        
        import secrets
        restore_code = secrets.token_urlsafe(32)
        
        from src.infrastructure.crypto.argon2_hasher import hash
        code_hash = hash(restore_code)
        
        insert_restore_code(backup_name, target_user['id'], code_hash)
        
        print("\n" + "="*60)
        print("SAVE THIS CODE NOW - IT WON'T BE SHOWN AGAIN!")
        print("="*60)
        print(f"Restore Code: {restore_code}")
        print("="*60)
        
    except ValidationError as e:
        print(f"Error: {e}")
    except Exception as e:
        print("Failed to generate restore code. Please try again.")


def restore_from_backup_flow():
    """Restore from backup using a code."""
    print("\n" + "-"*30)
    print("RESTORE FROM BACKUP")
    print("-"*30)
    
    try:
        backup_name = input("Backup name: ").strip()
        if not backup_name:
            print("Backup name cannot be empty.")
            return
        
        restore_code = input("Restore code: ").strip()
        if not restore_code:
            print("Restore code cannot be empty.")
            return
        
        from src.infrastructure.crypto.argon2_hasher import hash
        code_hash = hash(restore_code)
        
        success = consume_restore_code(1, backup_name, code_hash)
        
        if success:
            restore_from_backup(backup_name)
            print("Restore complete.")
        else:
            print("Invalid or used restore code.")
            
    except FileNotFoundError as e:
        print(f"Backup not found: {e}")
    except ValueError as e:
        print(f"Invalid backup: {e}")
    except Exception as e:
        print(f"Failed to restore from backup: {e}")
        print("Please try again.")


def view_logs(current_user: CurrentUser):
    """View audit logs."""
    print("\n" + "-"*30)
    print("AUDIT LOGS")
    print("-"*30)
    
    try:
        logs = read_all()
        
        if not logs:
            print("No logs found.")
            return
        
        print(f"\nShowing {len(logs)} log entries:")
        print("-" * 80)
        print(f"{'Date':<20} {'User':<15} {'Event':<20} {'Suspicious':<10}")
        print("-" * 80)
        
        for log_entry in logs:
            date_str = log_entry.get('ts', 'Unknown')[:19]
            user = log_entry.get('user', 'System')
            event = log_entry.get('event', 'Unknown')
            suspicious = "Yes" if log_entry.get('suspicious', False) else "No"
            
            print(f"{date_str:<20} {user:<15} {event:<20} {suspicious:<10}")
        
        mark_all_seen(current_user.id)
        print("\nMarked as read.")
        
    except Exception as e:
        print("Failed to read logs. Please try again.")
