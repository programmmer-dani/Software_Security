# src/domain/validators.py

import re
from datetime import datetime
from .errors import ValidationError
from .constants import CITIES, ROTTERDAM_BOUNDS

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

def validate_username(username: str) -> str:
    username = _clean_input(username, "Username")
    
    if not re.match(r'^[A-Za-z_][A-Za-z0-9_\'.]{7,10}$', username):
        raise ValidationError("Username must be 8-11 chars, start with letter/_ and use [a-z0-9_'.]")
    
    return username

def validate_password(password: str) -> str:
    password = _clean_input(password, "Password")
    
    if len(password) < 12 or len(password) > 30:
        raise ValidationError("Password must be 12-30 characters")
    
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain lowercase letter")
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain uppercase letter")
    
    if not re.search(r'[0-9]', password):
        raise ValidationError("Password must contain digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("Password must contain special character")
    
    return password

def validate_zip(zip_code: str) -> str:
    zip_code = _clean_input(zip_code, "Zip code")
    
    if not re.match(r'^\d{4}[A-Z]{2}$', zip_code):
        raise ValidationError("Zip code must be DDDDXX format (4 digits + 2 letters)")
    
    return zip_code

def validate_phone(phone: str) -> str:
    phone = _clean_input(phone, "Phone")
    
    if not re.match(r'^\d{8}$', phone):
        raise ValidationError("Phone must be exactly 8 digits")
    
    return phone

def validate_license(license_num: str) -> str:
    license_num = _clean_input(license_num, "License")
    
    if not re.match(r'^[A-Z]{2}\d{7}$|^[A-Z]\d{8}$', license_num):
        raise ValidationError("License must be 2 letters + 7 digits or 1 letter + 8 digits")
    
    return license_num

def validate_gender(gender: str) -> str:
    gender = _clean_input(gender, "Gender")
    
    if gender not in ['male', 'female', 'Male', 'Female', 'MALE', 'FEMALE']:
        raise ValidationError("Gender must be 'male' or 'female'")
    
    return gender

def validate_city(city: str) -> str:
    city = _clean_input(city, "City")
    
    # Case-insensitive city validation
    city_lower = city.lower()
    valid_cities_lower = [c.lower() for c in CITIES]
    
    if city_lower not in valid_cities_lower:
        raise ValidationError(f"City must be one of: {', '.join(CITIES)}")
    
    # Return the original case from CITIES list
    for valid_city in CITIES:
        if valid_city.lower() == city_lower:
            return valid_city
    
    return city  # fallback

def validate_birthday(birthday: str) -> str:
    birthday = _clean_input(birthday, "Birthday")
    
    try:
        datetime.strptime(birthday, '%Y-%m-%d')
    except ValueError:
        raise ValidationError("Birthday must be YYYY-MM-DD format")
    
    return birthday

def validate_soc(soc: int) -> int:
    if not isinstance(soc, int):
        raise ValidationError("SOC must be a number")
    
    if soc < 0 or soc > 100:
        raise ValidationError("SOC must be 0-100")
    
    return soc

def validate_latitude(lat: float) -> float:
    if not isinstance(lat, (int, float)):
        raise ValidationError("Latitude must be a number")
    
    if not (ROTTERDAM_BOUNDS["lat_min"] <= lat <= ROTTERDAM_BOUNDS["lat_max"]):
        raise ValidationError(f"Latitude must be {ROTTERDAM_BOUNDS['lat_min']}-{ROTTERDAM_BOUNDS['lat_max']}")
    
    return lat

def normalize_latitude(lat: float) -> float:
    """Normalize latitude to 5 decimal places for storage."""
    return round(lat, 5)

def validate_longitude(lon: float) -> float:
    if not isinstance(lon, (int, float)):
        raise ValidationError("Longitude must be a number")
    
    if not (ROTTERDAM_BOUNDS["lon_min"] <= lon <= ROTTERDAM_BOUNDS["lon_max"]):
        raise ValidationError(f"Longitude must be {ROTTERDAM_BOUNDS['lon_min']}-{ROTTERDAM_BOUNDS['lon_max']}")
    
    return lon

def normalize_longitude(lon: float) -> float:
    """Normalize longitude to 5 decimal places for storage."""
    return round(lon, 5)
