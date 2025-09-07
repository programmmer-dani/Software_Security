# src/infrastructure/db/traveller_repo_sqlite.py

from datetime import datetime
from .sqlite import get_conn
from infrastructure.crypto.fernet_box import encrypt, decrypt

def add(customer_id: str, first_name: str, last_name: str, birthday: str, gender: str,
        street: str, house_no: str, zip_code: str, city: str, email: str, phone: str, license: str):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO travellers (customer_id, first_name_enc, last_name_enc, birthday, gender,
                                  street_enc, house_no_enc, zip_enc, city, email_enc, phone_enc, license_enc, registered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_id,
            encrypt(first_name),
            encrypt(last_name),
            birthday,
            gender,
            encrypt(street),
            encrypt(house_no),
            encrypt(zip_code),
            city,
            encrypt(email),
            encrypt(phone),
            encrypt(license),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def all():
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM travellers")
        rows = cursor.fetchall()
        
        # Decrypt sensitive fields
        result = []
        for row in rows:
            result.append({
                'id': row[0],
                'customer_id': row[1],
                'first_name': decrypt(row[2]),
                'last_name': decrypt(row[3]),
                'birthday': row[4],
                'gender': row[5],
                'street': decrypt(row[6]),
                'house_no': decrypt(row[7]),
                'zip': decrypt(row[8]),
                'city': row[9],
                'email': decrypt(row[10]),
                'phone': decrypt(row[11]),
                'license': decrypt(row[12]),
                'registered_at': row[13]
            })
        
        return result
    finally:
        conn.close()
