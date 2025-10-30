

from .sqlite import db_connection, db_transaction
from src.infrastructure.crypto.fernet_box import encrypt

def add(customer_id: str, first_name: str, last_name: str, birthday: str, gender: str,
        street: str, house_no: str, zip_code: str, city: str, email: str, phone: str, license: str, registered_at: str):
    with db_transaction() as conn:
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
            registered_at
        ))
        
        return cursor.lastrowid

def all():
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM travellers")
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            result.append({
                'id': row[0],
                'customer_id': row[1],
                'first_name_enc': row[2],
                'last_name_enc': row[3],
                'birthday': row[4],
                'gender': row[5],
                'street_enc': row[6],
                'house_no_enc': row[7],
                'zip_enc': row[8],
                'city': row[9],
                'email_enc': row[10],
                'phone_enc': row[11],
                'license_enc': row[12],
                'registered_at': row[13]
            })
        
        return result

def get_by_id(traveller_id: int):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM travellers WHERE id = ?", (traveller_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
            
        return {
            'id': row[0],
            'customer_id': row[1],
            'first_name_enc': row[2],
            'last_name_enc': row[3],
            'birthday': row[4],
            'gender': row[5],
            'street_enc': row[6],
            'house_no_enc': row[7],
            'zip_enc': row[8],
            'city': row[9],
            'email_enc': row[10],
            'phone_enc': row[11],
            'license_enc': row[12],
            'registered_at': row[13]
        }

def update(traveller_id: int, **kwargs):
    with db_transaction() as conn:
        cursor = conn.cursor()
        
        
        cursor.execute("SELECT id FROM travellers WHERE id = ?", (traveller_id,))
        if not cursor.fetchone():
            return False
        
        
        update_fields = []
        values = []
        
        for field, value in kwargs.items():
            if field == 'first_name':
                update_fields.append('first_name_enc = ?')
                values.append(encrypt(value))
            elif field == 'last_name':
                update_fields.append('last_name_enc = ?')
                values.append(encrypt(value))
            elif field == 'street':
                update_fields.append('street_enc = ?')
                values.append(encrypt(value))
            elif field == 'house_no':
                update_fields.append('house_no_enc = ?')
                values.append(encrypt(value))
            elif field == 'zip_code':
                update_fields.append('zip_enc = ?')
                values.append(encrypt(value))
            elif field == 'email':
                update_fields.append('email_enc = ?')
                values.append(encrypt(value))
            elif field == 'phone':
                update_fields.append('phone_enc = ?')
                values.append(encrypt(value))
            elif field == 'license':
                update_fields.append('license_enc = ?')
                values.append(encrypt(value))
            elif field in ['birthday', 'gender', 'city']:
                update_fields.append(f'{field} = ?')
                values.append(value)
        
        if not update_fields:
            return False
        
        values.append(traveller_id)
        query = f"UPDATE travellers SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, values)
        
        return cursor.rowcount > 0

def delete(traveller_id: int):
    with db_transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM travellers WHERE id = ?", (traveller_id,))
        return cursor.rowcount > 0
