from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer , HTTPAuthorizationCredentials
from app.controllers.prescription_controllers import (
    create_prescription,
    get_prescription_by_id,
    get_prescriptions_by_doctor,
    get_prescriptions_by_patient,
    update_prescription,
    delete_prescription,
)
from app.models.prescription import PrescriptionCreate, PrescriptionUpdate
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
                status_code=403,
                detail={
                    "message": "Internal Server Error",
                    "exception": "403: Forbidden: Insufficient role"
                }
            )
    return dependency

@router.post('/', 
    description="Create a new prescription. Doctor access only.",
    response_description="Returns the created prescription data."
)
async def create_prescription_route(
    prescription_data: PrescriptionCreate,
    current_user: dict = Depends(resolve_user_temp(allowed_roles=["doctor"]))
):
    prescription_data.doctor_id = current_user["user_id"]
    return create_prescription(prescription_data)

@router.get('/{prescription_id}',
    description="Get prescription by ID.",
    response_description="Returns the prescription data."
)
async def get_prescription_route(
    prescription_id: int,
    current_user: dict = Depends(resolve_user_temp(allowed_roles=["doctor", "patient"]))
):
    return get_prescription_by_id(prescription_id, current_user)

@router.get('/doctor/{doctor_id}',
    description="Get all prescriptions by doctor ID.",
    response_description="Returns a list of prescriptions."
)
async def get_doctor_prescriptions_route(
    doctor_id: int,
    current_user: dict = Depends(resolve_user_temp(allowed_roles=["doctor"]))
):
    if current_user["user_id"] != doctor_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return get_prescriptions_by_doctor(doctor_id)

@router.get('/patient/{patient_id}',
    description="Get all prescriptions by patient ID.",
    response_description="Returns a list of prescriptions."
)
async def get_patient_prescriptions_route(
    patient_id: int,
    current_user: dict = Depends(resolve_user_temp(allowed_roles=["doctor", "patient"]))
):
    if current_user["role"] == "patient" and current_user["user_id"] != patient_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return get_prescriptions_by_patient(patient_id)

@router.put('/{prescription_id}',
    description="Update prescription. Doctor access only.",
    response_description="Returns the updated prescription data."
)
async def update_prescription_route(
    prescription_id: int,
    prescription_data: PrescriptionUpdate,
    current_user: dict = Depends(resolve_user_temp(allowed_roles=["doctor"]))
):
    return update_prescription(prescription_id, prescription_data, current_user["user_id"])

@router.delete('/{prescription_id}',
    description="Delete prescription. Doctor access only.",
    response_description="Returns success message."
)
async def delete_prescription_route(
    prescription_id: int,
    current_user: dict = Depends(resolve_user_temp(allowed_roles=["doctor"]))
):
    return delete_prescription(prescription_id, current_user["user_id"])