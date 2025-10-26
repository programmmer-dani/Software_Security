

def generate_customer_id(random_digits: str) -> str:

    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"CUST_{timestamp}{random_digits}"

def matches_partial(text: str, key: str) -> bool:

    if not text or not key:
        return False
    return key.lower() in text.lower()
