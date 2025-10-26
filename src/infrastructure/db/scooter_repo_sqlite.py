from src.infrastructure.db.sqlite import db_connection, db_transaction

def add(brand: str, model: str, serial_number: str, top_speed: int, 
        battery_capacity: int, soc: int, target_soc_min: int, target_soc_max: int,
        latitude: float, longitude: float, out_of_service: bool, mileage: int,
        last_maintenance_date: str, in_service_date: str, status: str = "active") -> int:
    with db_transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scooters (brand, model, serial_number, top_speed, battery_capacity, 
                               soc, target_soc_min, target_soc_max, latitude, longitude, 
                               out_of_service, mileage, last_maintenance_date, in_service_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (brand, model, serial_number, top_speed, battery_capacity, soc, 
              target_soc_min, target_soc_max, latitude, longitude, out_of_service, 
              mileage, last_maintenance_date, in_service_date, status))
        return cursor.lastrowid

def get_by_id(scooter_id: int):
    with db_transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scooters WHERE id = ?", (scooter_id,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'brand': row[1],
                'model': row[2],
                'serial_number': row[3],
                'top_speed': row[4],
                'battery_capacity': row[5],
                'soc': row[6],
                'target_soc_min': row[7],
                'target_soc_max': row[8],
                'latitude': row[9],
                'longitude': row[10],
                'out_of_service': row[11],
                'mileage': row[12],
                'last_maintenance_date': row[13],
                'in_service_date': row[14],
                'status': row[15]
            }
        return None

def get_by_serial(serial_number: str):
    with db_transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scooters WHERE serial_number = ?", (serial_number,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'brand': row[1],
                'model': row[2],
                'serial_number': row[3],
                'top_speed': row[4],
                'battery_capacity': row[5],
                'soc': row[6],
                'target_soc_min': row[7],
                'target_soc_max': row[8],
                'latitude': row[9],
                'longitude': row[10],
                'out_of_service': row[11],
                'mileage': row[12],
                'last_maintenance_date': row[13],
                'in_service_date': row[14],
                'status': row[15]
            }
        return None

def update(scooter_id: int, **kwargs) -> bool:
    if not kwargs:
        return False
    
    set_clauses = []
    values = []
    for key, value in kwargs.items():
        set_clauses.append(f"{key} = ?")
        values.append(value)
    
    values.append(scooter_id)
    
    with db_transaction() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE scooters 
            SET {', '.join(set_clauses)}
            WHERE id = ?
        """, values)
        return cursor.rowcount > 0

def search(search_term: str):
    with db_transaction() as conn:
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
                'top_speed': row[4],
                'battery_capacity': row[5],
                'soc': row[6],
                'target_soc_min': row[7],
                'target_soc_max': row[8],
                'latitude': row[9],
                'longitude': row[10],
                'out_of_service': row[11],
                'mileage': row[12],
                'last_maintenance_date': row[13],
                'in_service_date': row[14],
                'status': row[15]
            })
        return results

def all():
    with db_transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scooters ORDER BY id")
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'brand': row[1],
                'model': row[2],
                'serial_number': row[3],
                'top_speed': row[4],
                'battery_capacity': row[5],
                'soc': row[6],
                'target_soc_min': row[7],
                'target_soc_max': row[8],
                'latitude': row[9],
                'longitude': row[10],
                'out_of_service': row[11],
                'mileage': row[12],
                'last_maintenance_date': row[13],
                'in_service_date': row[14],
                'status': row[15]
            })
        return results

def delete(scooter_id: int) -> bool:
    with db_transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scooters WHERE id = ?", (scooter_id,))
        return cursor.rowcount > 0