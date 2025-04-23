from fastapi import APIRouter, Query, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.controllers.doctor_controllers import (
    get_all_doctors,
    get_doctor_by_id,
    update_doctor,
    search_doctors
)
from typing import Optional
from app.middlewares.verify_jwt import verify_jwt_temp

router = APIRouter()
security = HTTPBearer()

def resolve_user_temp(allowed_roles: list = None):
    async def dependency(credentials: HTTPAuthorizationCredentials = Depends(security)):
        try:
            access_token = credentials.credentials
            user = verify_jwt_temp(access_token, allowed_roles=allowed_roles)
            return user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Internal Server Error",
                    "exception": "403: Forbidden: Insufficient role"
                }
            )
    return dependency

@router.get('/',
    description="Fetch all doctors.",
    response_description="Returns a list of all doctors.",
    responses={
        200: {"description": "Doctors retrieved successfully"},
        404: {"description": "No doctors found"},
        500: {"description": "Internal server error"}
    }
)
def get_doctors():
    return get_all_doctors()

@router.get('/search',
    description="Search doctors with various filters.",
    response_description="Returns filtered list of doctors.",
    responses={
        200: {"description": "Search completed successfully"},
        404: {"description": "No doctors found matching criteria"},
        500: {"description": "Internal server error"}
    }
)

def search_doctors_route(
    speciality: Optional[str] = Query(None, description="Filter by speciality"),
    location: Optional[str] = Query(None, description="Filter by office location"),
    teleconsultation: Optional[bool] = Query(None, description="Filter by teleconsultation availability"),
    max_duration: Optional[int] = Query(None, gt=0, description="Maximum appointment duration in minutes"),
    user_latitude: Optional[float] = Query(None, description="User's latitude for geospatial filtering"),
    user_longitude: Optional[float] = Query(None, description="User's longitude for geospatial filtering")
):
    return search_doctors(
        speciality=speciality,
        location=location,
        teleconsultation=teleconsultation,
        max_duration=max_duration,
        user_latitude=user_latitude,
        user_longitude=user_longitude
    )

@router.get('/{doctor_id}',
    description="Fetch doctor details by ID.",
    response_description="Returns the doctor's data.",
    responses={
        200: {"description": "Doctor retrieved successfully"},
        404: {"description": "Doctor not found"},
        500: {"description": "Internal server error"}
    }
)
def get_doctor(doctor_id: int):
    return get_doctor_by_id(doctor_id)

@router.put('/{doctor_id}',
    description="Update doctor details.",
    response_description="Returns the updated doctor data.",
    responses={
        200: {"description": "Doctor updated successfully"},
        400: {"description": "Invalid input data"},
        404: {"description": "Doctor not found"},
        500: {"description": "Internal server error"}
    }
)
def update_doctor_route(
    doctor_id: int,
    doctor_data: dict,
    current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin", "doctor"]))
):
    # Check if user is updating their own profile or is an admin
    if current_user["role"] != "admin" and current_user["user_id"] != doctor_id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own profile unless you are an admin"
        )
    return update_doctor(doctor_id, doctor_data)

