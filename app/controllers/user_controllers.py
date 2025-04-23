from fastapi import APIRouter, HTTPException , UploadFile, File
from fastapi.requests import Request
from fastapi.responses import JSONResponse , Response
from app.database.database import User as us, db, Doctor, Patient , Admin
from app.config import settings
from datetime import datetime
import cloudinary
from cloudinary.uploader import upload
import bcrypt
from typing import Optional

cloudinary.config(
    cloud_name = settings.CLOUD_NAME,
    api_key =   settings.API_KEY,
    api_secret = settings.API_SECRET
)



def get_user_by_id(user_id:int):
    user = us.find(user_id=user_id)
    db.execute_query(user, params=(user_id,))
    user_data = db.fetch_one()
    user_data = {"user_id": user_data[0] ,"name": user_data[1] ,"refresh_token" : user_data[2], "email": user_data[3], "phone_number" : user_data[4], "date_of_birth" : user_data[5].isoformat() , "gender" : user_data[7] , "profile_picture_url" : user_data[8] ,"role": user_data[9]}
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return JSONResponse(content=user_data, status_code=200)

def get_all_users(email: Optional[str] = None, name: Optional[str] = None):
    try:
        query = "SELECT * FROM users WHERE 1=1"
        params = []
        
        if email:
            query += " AND LOWER(email) LIKE LOWER(%s)"
            params.append(f"%{email}%")
            
        if name:
            query += " AND LOWER(name) LIKE LOWER(%s)"
            params.append(f"%{name}%")
            
        query += ";"
        
        db.execute_query(query, params)
        result = db.fetch_all()
        
        users_data = [
            {
                "user_id": user[0],
                "name": user[1],
                "refresh_token": user[2],
                "email": user[3],
                "phone_number": user[4],
                "date_of_birth": user[5].isoformat() if user[5] else None,
                "gender": user[7],
                "profile_picture_url": user[8],
                "role": user[9]
            } 
            for user in result
        ]
        
        if not users_data:
            raise HTTPException(
                status_code=404, 
                detail="No users found matching the search criteria"
            )
            
        return JSONResponse(
            content={
                "total": len(users_data),
                "users": users_data
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


def get_user_by_email(request:Request):
    user_grabbed = request.headers.get("user")
    if not user_grabbed:
        raise HTTPException(status_code=403, detail="Access forbidden")
    email = user_grabbed.email
    
    user = us.find(email=email)
    db.execute_query(user, params=(email,))
    user_data = db.fetch_one()
    user_data = {"user_id": user_data[0] ,"name": user_data[1] ,"refresh_token" : user_data[2], "email": user_data[3], "phone_number" : user_data[4], "date_of_birth" : user_data[5].isoformat() if user_data[5] else None , "gender" : user_data[7] , "profile_picture_url" : user_data[8] ,"role": user_data[9]}
    print(user_data)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return JSONResponse(content=user_data, status_code=200)

def update_user(user_id: int, user_data: dict):
    user = us.find(user_id=user_id)
    db.execute_query(user, params=(user_id,))
    found_user = db.fetch_one()
    
    if not found_user:
        raise HTTPException(status_code=404, detail="User not found")

    doctor_fields = {
        "speciality", "experience", "max_appointments_in_day",
        "teleconsultation_available", "office_location", "office_location_url"
    }
    doctor_data = {k: user_data.pop(k) for k in doctor_fields if k in user_data}

    for field, idx in [("email", 3), ("phone_number", 4)]:
        if user_data.get(field) and user_data[field] != found_user[idx]:
            existing = us.find(**{field: user_data[field]})
            db.execute_query(existing, params=(user_data[field],))
            if db.fetch_one():
                raise HTTPException(status_code=400, detail=f"{field.replace('_', ' ').title()} already exists")

    if user_data.get("password"):
        user_data["password"] = bcrypt.hashpw(
            user_data["password"].encode('utf-8'), 
            bcrypt.gensalt(10)
        ).decode('utf-8')

    if user_data.get('date_of_birth'):
        user_data['date_of_birth'] = user_data['date_of_birth'].isoformat()

    if user_data.get("role") == "doctor" and doctor_data:
        doctor = Doctor.update(**doctor_data, user_id=user_id)
        db.execute_query(doctor, params=(*doctor_data.values(), user_id))

    user = us.update(**user_data, user_id=user_id)
    db.execute_query(user, params=(*user_data.values(), user_id))
    
    response_data = {**user_data, **doctor_data}
    return JSONResponse(content={"data": response_data}, status_code=200)
        
def delete_user(user_id:int):
    check_user = us.find(user_id=user_id)
    db.execute_query(check_user, params=(user_id,))
    if not db.fetch_one():
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        user = us.delete(user_id=user_id)
        db.execute_query(user, params=(user_id,))
        return JSONResponse(
            content={"message": "User deleted successfully", "user_id": user_id}, 
            status_code=200
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error deleting user: {str(e)}"
        )



def add_admin(user_id:int):
    check_user = us.find(user_id=user_id)
    db.execute_query(check_user, params=(user_id,))
    if not db.fetch_one():
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        admin = Admin.create(user_id=user_id, two_factor_auth_enabled=False, last_login=datetime.now().isoformat())
        db.execute_query(admin)
        user = us.update(role="admin", user_id=user_id)
        db.execute_query(user, params=("admin", user_id))
        return JSONResponse(
            content={"message": "Admin added successfully", "user_id": user_id}, 
            status_code=201
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error adding admin: {str(e)}"
        )

def switch_2fa_status(email:str):
    check_user = us.find(email=email)
    print(check_user)
    db.execute_query(check_user, params=(email,))
    user_found = db.fetch_one()
    if not user_found:
        raise HTTPException(status_code=404, detail="User not found")
    Admin_query = Admin.find(user_id=user_found[0])
    db.execute_query(Admin_query, params=(user_found[0],))
    admin_found = db.fetch_one()
    if not admin_found:
        raise HTTPException(status_code=404, detail="ONLY AVAILABLE FOR ADMINS!")
    
    try:
        twofa_enabled = admin_found[1]
        admin = Admin.update(two_factor_auth_enabled=not twofa_enabled, user_id=admin_found[0])
        db.execute_query(admin, params=(not twofa_enabled, admin_found[0]))
        status = "desactivated" if twofa_enabled else "activated"
        return JSONResponse(
            content={"message" : f"2FA {status} successfully", "user_id": admin_found[0]}, 
            status_code=200
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error activating 2FA (only available for admins): {str(e)}"
        )

def change_pfp(file: UploadFile, user_id:int):
    check_user = us.find(user_id=user_id)
    db.execute_query(check_user, params=(user_id,))
    user_found = db.fetch_one()
    if not user_found:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        result = upload(file.file)
        user = us.update(profile_picture_url=result["secure_url"], user_id=user_id)
        db.execute_query(user, params=(result["secure_url"], user_id))
        return JSONResponse(
            content=result["secure_url"], 
            status_code=200
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error updating profile picture: {str(e)}"
        )