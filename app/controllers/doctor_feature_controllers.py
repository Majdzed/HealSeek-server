from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.database.database import db
from datetime import datetime
from typing import Optional, List
from app.models.doctor_feature import AvailabilityBase, TimeOffBase

class DoctorAvailabilityController:
    @staticmethod
    def get_availability(doctor_id: int):
        try:
            query = """
                SELECT availability_id, day_of_week, start_time, end_time, is_available 
                FROM doctor_availability 
                WHERE doctor_id = %s 
                ORDER BY day_of_week, start_time;
            """
            db.execute_query(query, (doctor_id,))
            availabilities = db.fetch_all()
            
            if not availabilities:
                return JSONResponse(content={"availabilities": []}, status_code=200)
                
            return JSONResponse(
                content={
                    "availabilities": [
                        {
                            "availability_id": a[0],
                            "day_of_week": a[1],
                            "start_time": a[2].strftime("%H:%M"),
                            "end_time": a[3].strftime("%H:%M"),
                            "is_available": a[4]
                        } for a in availabilities
                    ]
                },
                status_code=200
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def create_availability(doctor_id: int, availability: AvailabilityBase):
        try:
            query = """
                INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time, is_available)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING availability_id;
            """
            db.execute_query(
                query,
                (doctor_id, availability.day_of_week, availability.start_time, 
                 availability.end_time, availability.is_available)
            )
            availability_id = db.fetch_one()[0]
            
            return JSONResponse(
                content={"message": "Availability created", "availability_id": availability_id},
                status_code=201
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def update_availability(availability_id: int, doctor_id: int, availability: AvailabilityBase):
        try:
            query = """
                UPDATE doctor_availability 
                SET day_of_week = %s, start_time = %s, end_time = %s, is_available = %s
                WHERE availability_id = %s AND doctor_id = %s;
            """
            db.execute_query(
                query,
                (availability.day_of_week, availability.start_time, availability.end_time,
                 availability.is_available, availability_id, doctor_id)
            )
            
            if db.get_rowcount() == 0:
                raise HTTPException(status_code=404, detail="Availability not found")
                
            return JSONResponse(
                content={"message": "Availability updated"},
                status_code=200
            )
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def delete_availability(availability_id: int, doctor_id: int):
        try:
            query = "DELETE FROM doctor_availability WHERE availability_id = %s AND doctor_id = %s;"
            db.execute_query(query, (availability_id, doctor_id))
            
            if db.get_rowcount() == 0:
                raise HTTPException(status_code=404, detail="Availability not found")
                
            return JSONResponse(
                content={"message": "Availability deleted"},
                status_code=200
            )
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

class DoctorTimeOffController:
    @staticmethod
    def get_time_off(doctor_id: int):
        try:
            query = """
                SELECT time_off_id, start_datetime, end_datetime, reason 
                FROM doctor_time_off 
                WHERE doctor_id = %s 
                ORDER BY start_datetime;
            """
            db.execute_query(query, (doctor_id,))
            time_offs = db.fetch_all()
            
            return JSONResponse(
                content={
                    "time_offs": [
                        {
                            "time_off_id": t[0],
                            "start_datetime": t[1].isoformat(),
                            "end_datetime": t[2].isoformat(),
                            "reason": t[3]
                        } for t in time_offs
                    ]
                },
                status_code=200
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def create_time_off(doctor_id: int, time_off: TimeOffBase):
        try:
            query = """
                INSERT INTO doctor_time_off (doctor_id, start_datetime, end_datetime, reason)
                VALUES (%s, %s, %s, %s)
                RETURNING time_off_id;
            """
            db.execute_query(
                query,
                (doctor_id, time_off.start_datetime, time_off.end_datetime, time_off.reason)
            )
            time_off_id = db.fetch_one()[0]
            
            return JSONResponse(
                content={"message": "Time off created", "time_off_id": time_off_id},
                status_code=201
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def update_time_off(time_off_id: int, doctor_id: int, time_off: TimeOffBase):
        try:
            query = """
                UPDATE doctor_time_off 
                SET start_datetime = %s, end_datetime = %s, reason = %s
                WHERE time_off_id = %s AND doctor_id = %s;
            """
            db.execute_query(
                query,
                (time_off.start_datetime, time_off.end_datetime, time_off.reason,
                 time_off_id, doctor_id)
            )
            
            if db.get_rowcount() == 0:
                raise HTTPException(status_code=404, detail="Time off not found")
                
            return JSONResponse(
                content={"message": "Time off updated"},
                status_code=200
            )
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def delete_time_off(time_off_id: int, doctor_id: int):
        try:
            query = "DELETE FROM doctor_time_off WHERE time_off_id = %s AND doctor_id = %s;"
            db.execute_query(query, (time_off_id, doctor_id))
            
            if db.get_rowcount() == 0:
                raise HTTPException(status_code=404, detail="Time off not found")
                
            return JSONResponse(
                content={"message": "Time off deleted"},
                status_code=200
            )
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

class DoctorLanguagesController:
    @staticmethod
    def get_languages(doctor_id: int):
        try:
            query = """
                SELECT l.language_id, l.language_name
                FROM languages l
                JOIN doctor_languages dl ON l.language_id = dl.language_id
                WHERE dl.doctor_id = %s;
            """
            db.execute_query(query, (doctor_id,))
            languages = db.fetch_all()
            
            return JSONResponse(
                content={
                    "languages": [
                        {"language_id": l[0], "language_name": l[1]}
                        for l in languages
                    ]
                },
                status_code=200
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def add_language(doctor_id: int, language_id: int):
        try:
            query = """
                INSERT INTO doctor_languages (doctor_id, language_id)
                VALUES (%s, %s);
            """
            db.execute_query(query, (doctor_id, language_id))
            
            return JSONResponse(
                content={"message": "Language added"},
                status_code=201
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def remove_language(doctor_id: int, language_id: int):
        try:
            query = """
                DELETE FROM doctor_languages 
                WHERE doctor_id = %s AND language_id = %s;
            """
            db.execute_query(query, (doctor_id, language_id))
            
            if db.get_rowcount() == 0:
                raise HTTPException(status_code=404, detail="Language not found")
                
            return JSONResponse(
                content={"message": "Language removed"},
                status_code=200
            )
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

class DoctorInsuranceController:
    @staticmethod
    def get_insurance(doctor_id: int):
        try:
            query = """
                SELECT it.insurance_type_id, it.type_name
                FROM insurance_types it
                JOIN doctor_insurance di ON it.insurance_type_id = di.insurance_type_id
                WHERE di.doctor_id = %s;
            """
            db.execute_query(query, (doctor_id,))
            insurances = db.fetch_all()
            
            return JSONResponse(
                content={
                    "insurance_types": [
                        {"insurance_type_id": i[0], "type_name": i[1]}
                        for i in insurances
                    ]
                },
                status_code=200
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def add_insurance(doctor_id: int, insurance_type_id: int):
        try:
            query = """
                INSERT INTO doctor_insurance (doctor_id, insurance_type_id)
                VALUES (%s, %s);
            """
            db.execute_query(query, (doctor_id, insurance_type_id))
            
            return JSONResponse(
                content={"message": "Insurance type added"},
                status_code=201
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def remove_insurance(doctor_id: int, insurance_type_id: int):
        try:
            query = """
                DELETE FROM doctor_insurance 
                WHERE doctor_id = %s AND insurance_type_id = %s;
            """
            db.execute_query(query, (doctor_id, insurance_type_id))
            
            if db.get_rowcount() == 0:
                raise HTTPException(status_code=404, detail="Insurance type not found")
                
            return JSONResponse(
                content={"message": "Insurance type removed"},
                status_code=200
            )
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))