# src/domain/services.py

import re

def generate_customer_id(random_digits: str) -> str:
    """Generate a customer ID with the format CUST_YYYYMMDDHHMMSS + random digits."""
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"CUST_{timestamp}{random_digits}"

def matches_partial(text: str, key: str) -> bool:
    """Check if key matches text partially (case-insensitive)."""
    if not text or not key:
        return False
    return key.lower() in text.lower()
