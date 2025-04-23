from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.doctor_feature import AvailabilityBase, TimeOffBase, LanguageBase, InsuranceBase
from app.controllers.doctor_feature_controllers import (
    DoctorAvailabilityController,
    DoctorTimeOffController,
    DoctorLanguagesController,
    DoctorInsuranceController
)
from app.middlewares.verify_jwt import verify_jwt_temp

router = APIRouter(tags=["doctor-features"])
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
                detail="Insufficient permissions"
            )
    return dependency

# Availability Routes
@router.get("/{doctor_id}/availability",
    description="Get doctor's availability schedule",
    response_description="List of doctor's availability slots"
)
async def get_availability(doctor_id: int):
    return DoctorAvailabilityController.get_availability(doctor_id)

@router.post("/{doctor_id}/availability",
    description="Add new availability slot",
    response_description="Created availability details"
)
async def create_availability(
    doctor_id: int,
    availability: AvailabilityBase,
    current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin", "doctor"]))
):
    if current_user["role"] != "admin" and current_user["user_id"] != doctor_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this doctor's availability")
    return DoctorAvailabilityController.create_availability(doctor_id, availability)

@router.put("/{doctor_id}/availability/{availability_id}",
    description="Update existing availability slot",
    response_description="Updated availability details"
)
@router.put("/{doctor_id}/availability/{availability_id}",
    description="Update existing availability slot",
    response_description="Updated availability details"
)
async def update_availability(
    doctor_id: int,
    availability_id: int,
    availability: AvailabilityBase,
    current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin", "doctor"]))
):
    if current_user["role"] != "admin" and current_user["user_id"] != doctor_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this doctor's availability")
    return DoctorAvailabilityController.update_availability(availability_id, doctor_id, availability)

@router.delete("/{doctor_id}/availability/{availability_id}",
    description="Delete availability slot",
    response_description="Deletion confirmation"
)
async def delete_availability(
    doctor_id: int,
    availability_id: int,
    current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin", "doctor"]))
):
    if current_user["role"] != "admin" and current_user["user_id"] != doctor_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this doctor's availability")
    return DoctorAvailabilityController.delete_availability(availability_id, doctor_id)

@router.get("/{doctor_id}/time-off",
    description="Get doctor's time off schedule",
    response_description="List of doctor's time off periods"
)
async def get_time_off(doctor_id: int):
    return DoctorTimeOffController.get_time_off(doctor_id)

@router.post("/{doctor_id}/time-off",
    description="Add new time off period",
    response_description="Created time off details"
)
async def create_time_off(
    doctor_id: int,
    time_off: TimeOffBase,
    current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin", "doctor"]))
):
    if current_user["role"] != "admin" and current_user["user_id"] != doctor_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this doctor's time off")
    return DoctorTimeOffController.create_time_off(doctor_id, time_off)

@router.put("/{doctor_id}/time-off/{time_off_id}",
    description="Update existing time off period",
    response_description="Updated time off details"
)
async def update_time_off(
    doctor_id: int,
    time_off_id: int,
    time_off: TimeOffBase,
    current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin", "doctor"]))
):
    if current_user["role"] != "admin" and current_user["user_id"] != doctor_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this doctor's time off")
    return DoctorTimeOffController.update_time_off(time_off_id, doctor_id, time_off)

@router.delete("/{doctor_id}/time-off/{time_off_id}",
    description="Delete time off period",
    response_description="Deletion confirmation"
)
async def delete_time_off(
    doctor_id: int,
    time_off_id: int,
    current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin", "doctor"]))
):
    if current_user["role"] != "admin" and current_user["user_id"] != doctor_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this doctor's time off")
    return DoctorTimeOffController.delete_time_off(time_off_id, doctor_id)

@router.get("/{doctor_id}/languages",
    description="Get doctor's languages",
    response_description="List of doctor's languages"
)
async def get_languages(doctor_id: int):
    return DoctorLanguagesController.get_languages(doctor_id)

@router.post("/{doctor_id}/languages/{language_id}",
    description="Add language to doctor's profile",
    response_description="Language addition confirmation"
)
async def add_language(
    doctor_id: int,
    language_id: int,
    current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin", "doctor"]))
):
    if current_user["role"] != "admin" and current_user["user_id"] != doctor_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this doctor's languages")
    return DoctorLanguagesController.add_language(doctor_id, language_id)

@router.delete("/{doctor_id}/languages/{language_id}",
    description="Remove language from doctor's profile",
    response_description="Language removal confirmation"
)
async def remove_language(
    doctor_id: int,
    language_id: int,
    current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin", "doctor"]))
):
    if current_user["role"] != "admin" and current_user["user_id"] != doctor_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this doctor's languages")
    return DoctorLanguagesController.remove_language(doctor_id, language_id)

# Insurance Routes
@router.get("/{doctor_id}/insurance",
    description="Get doctor's accepted insurance types",
    response_description="List of doctor's insurance types"
)
async def get_insurance(doctor_id: int):
    return DoctorInsuranceController.get_insurance(doctor_id)

@router.post("/{doctor_id}/insurance/{insurance_type_id}",
    description="Add insurance type to doctor's profile",
    response_description="Insurance type addition confirmation"
)
async def add_insurance(
    doctor_id: int,
    insurance_type_id: int,
    current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin", "doctor"]))
):
    if current_user["role"] != "admin" and current_user["user_id"] != doctor_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this doctor's insurance types")
    return DoctorInsuranceController.add_insurance(doctor_id, insurance_type_id)

@router.delete("/{doctor_id}/insurance/{insurance_type_id}",
    description="Remove insurance type from doctor's profile",
    response_description="Insurance type removal confirmation"
)
async def remove_insurance(
    doctor_id: int,
    insurance_type_id: int,
    current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin", "doctor"]))
):
    if current_user["role"] != "admin" and current_user["user_id"] != doctor_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this doctor's insurance types")
    return DoctorInsuranceController.remove_insurance(doctor_id, insurance_type_id)
