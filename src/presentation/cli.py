import sys
from datetime import datetime
from typing import Optional

from src.application.security.acl import CurrentUser
from src.domain.errors import ValidationError
from src.domain.validators import (
    validate_username, validate_password, validate_zip, validate_phone,
    validate_license, validate_gender, validate_city, validate_birthday
)
from src.domain.constants import ROLES


def run(app):
    """Main application entry point."""
    current_user: Optional[CurrentUser] = None
    
    while True:
        if current_user is None:
            current_user = main_menu(app)
        else:
            current_user = role_menu(app, current_user)


def main_menu(app) -> Optional[CurrentUser]:
    """Main menu for unauthenticated users."""
    while True:
        print("\n" + "="*50)
        print("UM Members Management System")
        print("="*50)
        print("1) Login")
        print("2) Exit")
        
        choice = input("\nChoose option (1-2): ").strip()
        
        if choice == "1":
            return login_flow(app)
        elif choice == "2":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid option. Please choose 1 or 2.")


def login_flow(app) -> Optional[CurrentUser]:
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
        
        user = app.login(username, password)
        
        if user:
            print(f"\nWelcome, {user.role}!")
            
            if user.role in [ROLES[0], ROLES[1]]:  # SUPER_ADMIN, SYS_ADMIN
                unread_count = app.get_unread_suspicious_count(user)
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


def role_menu(app, current_user: CurrentUser) -> Optional[CurrentUser]:
    """Role-based menu system."""
    if current_user.role == ROLES[0]:  # SUPER_ADMIN
        return super_admin_menu(app, current_user)
    elif current_user.role == ROLES[1]:  # SYS_ADMIN
        return sys_admin_menu(app, current_user)
    elif current_user.role == ROLES[2]:  # ENGINEER
        return engineer_menu(app, current_user)
    else:
        print("Access denied. Unknown role.")
        return None


def super_admin_menu(app, current_user: CurrentUser) -> Optional[CurrentUser]:
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
            create_system_admin(app, current_user)
        elif choice == "B":
            generate_restore_code(app, current_user)
        elif choice == "C":
            create_backup_flow(app, current_user)
        elif choice == "D":
            view_logs(app, current_user)
        elif choice == "E":
            return None
        else:
            print("Invalid option. Please choose A-E.")


def sys_admin_menu(app, current_user: CurrentUser) -> Optional[CurrentUser]:
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
            change_password_flow(app, current_user)
        elif choice == "B":
            add_traveller_flow(app, current_user)
        elif choice == "C":
            search_traveller_flow(app, current_user)
        elif choice == "D":
            restore_from_backup_flow(app, current_user)
        elif choice == "E":
            create_backup_flow(app, current_user)
        elif choice == "F":
            view_logs(app, current_user)
        elif choice == "G":
            return None
        else:
            print("Invalid option. Please choose A-G.")


def engineer_menu(app, current_user: CurrentUser) -> Optional[CurrentUser]:
    """Engineer menu."""
    while True:
        print("\n" + "="*50)
        print("ENGINEER MENU")
        print("="*50)
        print("A) Change My Password")
        print("B) Add Traveller")
        print("C) Search Traveller")
        print("D) Logout")
        
        choice = input("\nChoose option (A-D): ").strip().upper()
        
        if choice == "A":
            change_password_flow(app, current_user)
        elif choice == "B":
            add_traveller_flow(app, current_user)
        elif choice == "C":
            search_traveller_flow(app, current_user)
        elif choice == "D":
            return None
        else:
            print("Invalid option. Please choose A-D.")


def create_system_admin(app, current_user: CurrentUser):
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
        
        app.create_sys_admin(current_user, username, password, first_name, last_name)
        print("System Admin created successfully!")
        
    except ValidationError as e:
        print(f"Error: {e}")
    except Exception as e:
        print("Failed to create System Admin. Please try again.")


def change_password_flow(app, current_user: CurrentUser):
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
        
        app.change_password(current_user, old_password, new_password)
        print("Password changed successfully!")
        
    except ValidationError as e:
        print(f"Error: {e}")
    except Exception as e:
        print("Failed to change password. Please try again.")


def add_traveller_flow(app, current_user: CurrentUser):
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
        
        customer_id = app.add_traveller(
            current_user=current_user,
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
            license_no=license_no
        )
        print(f"Traveller added successfully! Customer ID: {customer_id}")
        
    except ValidationError as e:
        print(f"Error: {e}")
    except Exception as e:
        print("Failed to add traveller. Please try again.")


def search_traveller_flow(app, current_user: CurrentUser):
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
        matches = app.search_travellers(current_user, search_term)
        
        if matches:
            print(f"\nFound {len(matches)} traveller(s):")
            print("-" * 60)
            for traveller in matches:
                first_name = app.crypto.decrypt(traveller['first_name_enc'])
                last_name = app.crypto.decrypt(traveller['last_name_enc'])
                print(f"ID: {traveller['id']} | Customer: {traveller['customer_id']} | Name: {first_name} {last_name}")
        else:
            print("No travellers found matching your search.")
            
    except Exception as e:
        print("Failed to search travellers. Please try again.")


def create_backup_flow(app, current_user: CurrentUser):
    """Create a backup."""
    print("\n" + "-"*30)
    print("CREATE BACKUP")
    print("-"*30)
    
    try:
        backup_name = app.create_backup(current_user)
        print(f"Backup created: {backup_name}")
        
    except Exception as e:
        print(f"Failed to create backup: {e}")
        print("Please try again.")


def generate_restore_code(app, current_user: CurrentUser):
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
        
        restore_code = app.generate_restore_code(current_user, backup_name, target_username)
        
        print("\n" + "="*60)
        print("SAVE THIS CODE NOW - IT WON'T BE SHOWN AGAIN!")
        print("="*60)
        print(f"Restore Code: {restore_code}")
        print("="*60)
        
    except ValidationError as e:
        print(f"Error: {e}")
    except Exception as e:
        print("Failed to generate restore code. Please try again.")


def restore_from_backup_flow(app, current_user: CurrentUser):
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
        
        success = app.restore_with_code(current_user, backup_name, restore_code)
        
        if success:
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


def view_logs(app, current_user: CurrentUser):
    """View audit logs."""
    print("\n" + "-"*30)
    print("AUDIT LOGS")
    print("-"*30)
    
    try:
        logs = app.view_logs(current_user)
        
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
        
        app.mark_all_seen(current_user)
        print("\nMarked as read.")
        
    except Exception as e:
        print("Failed to read logs. Please try again.")
