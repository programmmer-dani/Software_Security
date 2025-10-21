# src/infrastructure/db/scooter_repo_sqlite.py

import sqlite3
from src.infrastructure.db.sqlite import db_connection

def add(brand: str, model: str, serial_number: str, max_speed: int, 
        battery_capacity: int, soc: int, latitude: float, longitude: float, 
        in_service_date: str, status: str = "active") -> int:
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scooters (brand, model, serial_number, max_speed, battery_capacity, 
                               soc, latitude, longitude, in_service_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (brand, model, serial_number, max_speed, battery_capacity, 
              soc, latitude, longitude, in_service_date, status))
        return cursor.lastrowid

def get_by_id(scooter_id: int):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scooters WHERE id = ?", (scooter_id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            'id': row[0],
            'brand': row[1],
            'model': row[2],
            'serial_number': row[3],
            'max_speed': row[4],
            'battery_capacity': row[5],
            'soc': row[6],
            'latitude': row[7],
            'longitude': row[8],
            'in_service_date': row[9],
            'status': row[10]
        }

def get_by_serial(serial_number: str):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scooters WHERE serial_number = ?", (serial_number,))
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            'id': row[0],
            'brand': row[1],
            'model': row[2],
            'serial_number': row[3],
            'max_speed': row[4],
            'battery_capacity': row[5],
            'soc': row[6],
            'latitude': row[7],
            'longitude': row[8],
            'in_service_date': row[9],
            'status': row[10]
        }

def update(scooter_id: int, **kwargs) -> bool:
    if not kwargs:
        return False
    
    # Build dynamic update query
    set_clauses = []
    values = []
    
    for field, value in kwargs.items():
        if field in ['brand', 'model', 'serial_number', 'max_speed', 'battery_capacity', 
                     'soc', 'latitude', 'longitude', 'in_service_date', 'status']:
            set_clauses.append(f"{field} = ?")
            values.append(value)
    
    if not set_clauses:
        return False
    
    values.append(scooter_id)
    
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE scooters 
            SET {', '.join(set_clauses)}
            WHERE id = ?
        """, values)
        return cursor.rowcount > 0

def search(search_term: str):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM scooters 
            WHERE brand LIKE ? OR model LIKE ? OR serial_number LIKE ? OR status LIKE ?
        """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'brand': row[1],
                'model': row[2],
                'serial_number': row[3],
                'max_speed': row[4],
                'battery_capacity': row[5],
                'soc': row[6],
                'latitude': row[7],
                'longitude': row[8],
                'in_service_date': row[9],
                'status': row[10]
            })
        return results

def all():
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scooters ORDER BY id")
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'brand': row[1],
                'model': row[2],
                'serial_number': row[3],
                'max_speed': row[4],
                'battery_capacity': row[5],
                'soc': row[6],
                'latitude': row[7],
                'longitude': row[8],
                'in_service_date': row[9],
                'status': row[10]
            })
        return results

def delete(scooter_id: int) -> bool:
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scooters WHERE id = ?", (scooter_id,))
        return cursor.rowcount > 0
