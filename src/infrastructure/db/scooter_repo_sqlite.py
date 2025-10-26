

from src.infrastructure.db.sqlite import db_connection

def add(brand: str, model: str, serial_number: str, top_speed: int, 
        battery_capacity: int, soc: int, target_soc_min: int, target_soc_max: int,
        latitude: float, longitude: float, out_of_service: bool, mileage: int,
        last_maintenance_date: str, in_service_date: str, status: str = "active") -> int:
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scooters (brand, model, serial_number, top_speed, battery_capacity, 
                               soc, target_soc_min, target_soc_max, latitude, longitude, 
                               out_of_service, mileage, last_maintenance_date, in_service_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            UPDATE scooters 
            SET {', '.join(set_clauses)}
            WHERE id = ?

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
