from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.database.database import Doctor, db
from typing import Optional
from typing import List, Dict
from haversine import haversine, Unit

def get_all_doctors():
    try:
        query = """
            SELECT u.*, d.*
            FROM users u
            JOIN doctors d ON u.user_id = d.user_id
            WHERE u.role = 'doctor';
        """
        db.execute_query(query)
        result = db.fetch_all()
        doctors_data = [
            {
                "user_id": doc[0],
                "name": doc[1],
                "email": doc[3],
                "phone_number": doc[4],
                "date_of_birth": doc[5].isoformat() if doc[5] else None,
                "gender": doc[7],
                "profile_picture_url": doc[8],
                "speciality": doc[11],
                "experience": doc[12],
                "max_appointments_per_day": doc[13],
                "appointment_duration_minutes": doc[14],
                "teleconsultation_available": doc[15],
                "office_location": doc[16],
                "office_location_url": doc[17]
            }
            for doc in result
        ]
        
        if not doctors_data:
            raise HTTPException(
                status_code=404,
                detail="No doctors found"
            )
            
        return JSONResponse(
            content={
                "total": len(doctors_data),
                "doctors": doctors_data
            },
            status_code=200
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

def get_doctor_by_id(doctor_id: int):
    try:
        query = """
            SELECT u.*, d.*
            FROM users u
            JOIN doctors d ON u.user_id = d.user_id
            WHERE u.user_id = %s AND u.role = 'doctor';
        """
        db.execute_query(query, params=(doctor_id,))
        result = db.fetch_one()
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Doctor not found"
            )
            
        doctor_data = {
            "user_id": result[0],
            "name": result[1],
            "email": result[3],
            "phone_number": result[4],
            "date_of_birth": result[5].isoformat() if result[5] else None,
            "gender": result[7],
            "profile_picture_url": result[8],
            "speciality": result[11],
            "experience": result[12],
            "max_appointments_per_day": result[13],
            "appointment_duration_minutes": result[14],
            "teleconsultation_available": result[15],
            "office_location": result[16],
            "office_location_url": result[17]
        }
        
        return JSONResponse(content=doctor_data, status_code=200)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

def update_doctor(doctor_id: int, doctor_data: dict):
    try:
        # First check if doctor exists
        query = """
            SELECT 1 FROM users u
            JOIN doctors d ON u.user_id = d.user_id
            WHERE u.user_id = %s AND u.role = 'doctor';
        """
        db.execute_query(query, params=(doctor_id,))
        if not db.fetch_one():
            raise HTTPException(status_code=404, detail="Doctor not found")

        # Update doctor-specific fields
        doctor_fields = {
            "speciality",
            "experience",
            "max_appointments_per_day",
            "appointment_duration_minutes",
            "teleconsultation_available",
            "office_location",
            "office_location_url"
        }
        doctor_updates = {k: v for k, v in doctor_data.items() if k in doctor_fields}
        
        if "experience" in doctor_updates and doctor_updates["experience"] < 0:
            raise HTTPException(status_code=400, detail="Experience cannot be negative")
        
        if "max_appointments_per_day" in doctor_updates and doctor_updates["max_appointments_per_day"] <= 0:
            raise HTTPException(status_code=400, detail="Maximum appointments per day must be positive")
            
        if "appointment_duration_minutes" in doctor_updates and doctor_updates["appointment_duration_minutes"] <= 0:
            raise HTTPException(status_code=400, detail="Appointment duration must be positive")

        if doctor_updates:
            update_query = Doctor.update(**doctor_updates, user_id=doctor_id)
            db.execute_query(update_query, params=(*doctor_updates.values(), doctor_id))

        return JSONResponse(
            content={"message": "Doctor updated successfully", "updated_fields": doctor_updates},
            status_code=200
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating doctor: {str(e)}"
        )



def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two coordinates in kilometers.
    """
    print("eeeeeeeeeeeeeeeeeeeeeeeeeee",haversine((lat1, lon1), (lat2, lon2), unit=Unit.KILOMETERS))
    return haversine((lat1, lon1), (lat2, lon2), unit=Unit.KILOMETERS)

def search_doctors(
    speciality: Optional[str] = None,
    location: Optional[str] = None,
    teleconsultation: Optional[bool] = None,
    max_duration: Optional[int] = None,
    user_latitude: Optional[float] = None,
    user_longitude: Optional[float] = None
):
    try:
        # Fetch all doctors from the database
        query = """
            SELECT u.*, d.*
            FROM users u
            JOIN doctors d ON u.user_id = d.user_id
            WHERE u.role = 'doctor'
        """
        params = []
        
        if speciality:
            query += " AND LOWER(d.speciality) LIKE LOWER(%s)"
            params.append(f"%{speciality}%")
            
        if location:
            query += " AND LOWER(d.office_location) LIKE LOWER(%s)"
            params.append(f"%{location}%")
            
        if teleconsultation is not None:
            query += " AND d.teleconsultation_available = %s"
            params.append(teleconsultation)
            
        if max_duration is not None:
            query += " AND d.appointment_duration_minutes <= %s"
            params.append(max_duration)
            
        query += " ORDER BY d.experience DESC, u.name ASC"
        
        db.execute_query(query, params)
        result = db.fetch_all()
        
        doctors_data = [
            {
                "user_id": doc[0],
                "name": doc[1],
                "email": doc[3],
                "phone_number": doc[4],
                "date_of_birth": doc[5].isoformat() if doc[5] else None,
                "gender": doc[7],
                "profile_picture_url": doc[8],
                "speciality": doc[11],
                "experience": doc[12],
                "max_appointments_per_day": doc[13],
                "appointment_duration_minutes": doc[14],
                "teleconsultation_available": doc[15],
                "office_location": doc[16],
                "office_location_url": doc[17]
            }
            for doc in result
        ]
        
        # Filter doctors within a 2km radius (if user coordinates are provided)
        if user_latitude is not None and user_longitude is not None and user_latitude != 0 and user_longitude != 0:
            filtered_doctors = []
            for doctor in doctors_data:
                if doctor["office_location_url"]:
                    # Extract latitude and longitude from office_location_url
                    doctor_latitude, doctor_longitude = map(float, doctor["office_location_url"].split(','))
                    print(doctor_latitude, doctor_longitude)
                    # Calculate the distance
                    distance = calculate_distance(
                        user_latitude, user_longitude,
                        doctor_latitude, doctor_longitude
                    )
                    print("hadi distance",distance)
                    
                    # Add the doctor if within 2km
                    if distance <= 4:
                        doctor["distance"] = distance  # Add distance to the doctor's data
                        filtered_doctors.append(doctor)
                        print(doctor)
            
            doctors_data = filtered_doctors
        
        if not doctors_data:
            raise HTTPException(
                status_code=404,
                detail="No doctors found matching the search criteria"
            )
            
        return {
            "total": len(doctors_data),
            "doctors": doctors_data
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )