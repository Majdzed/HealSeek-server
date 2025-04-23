from fastapi import APIRouter , Request , Depends
from app.controllers.insurance_type_controllers import get_all_insurance_types as get_insurances , add_insurance_type as add_insurance , update_insurance_type as update_insurance , get_insurance_type_by_id , get_insurance_type_by_name , delete_insurance_type as delete_insurance
from app.controllers.insurance_type_controllers import add_insurance_to_doctor_using_insurance_id , add_insurance_to_doctor_using_insurance_name, get_all_insurance_types_of_doctor,delete_insurance_from_doctor , get_all_doctors_of_insurance,get_all_doctors_of_insurance_type_by_name , get_all_insurances_of_doctors
from app.models.insurance_type import Insurance ,DoctorInsurance,DoctorInsurance2
from app.routes.user_routes import resolve_user


router = APIRouter()

@router.get('/all')
def get_all_insurance_types():
    return get_insurances()

@router.post('/add' , dependencies=[Depends(resolve_user(allowed_roles=["admin"]))])
def add_insurance_type(insurance: Insurance):
    return add_insurance(insurance)

@router.put('/update/{insurance_id}' , dependencies=[Depends(resolve_user(allowed_roles=["admin"]))])
def update_insurance_type(insurance_id:int , insurance_data:dict):
    return update_insurance(insurance_id , insurance_data)

@router.get('/get_by_id/{insurance_id}')
def get_insurance_by_id(insurance_id:int):
    return get_insurance_type_by_id(insurance_id)

@router.get('/get_by_name/{insurance_name}')
def get_insurance_by_name(insurance_name:str):
    return get_insurance_type_by_name(insurance_name)

@router.delete('/delete_by_id/{insurance_id}' , dependencies=[Depends(resolve_user(allowed_roles=["admin"]))])
def delete_insurance_type(insurance_id:int):
    return delete_insurance(insurance_id)

@router.post('/doctor/add_by_id' ,dependencies=[Depends(resolve_user(allowed_roles=["doctor"]))])
def add_insurance_to_doctor_by_id(insurance:DoctorInsurance):
    return add_insurance_to_doctor_using_insurance_id(insurance)

@router.post('/doctor/add_by_name', dependencies=[Depends(resolve_user(allowed_roles=["doctor"]))])
def add_insurance_to_doctor_by_name(insurance:DoctorInsurance2):
    return add_insurance_to_doctor_using_insurance_name(insurance)

@router.get('/doctor/all_insurances' ,dependencies=[Depends(resolve_user(allowed_roles=["doctor"]))])
def get_all_insurance_types_of_doc(request : Request):
    doctor_id = request.state.user
    return get_all_insurance_types_of_doctor(doctor_id)

@router.delete('/doctor/delete_insurance' , dependencies=[Depends(resolve_user(allowed_roles=["doctor"]))])
def delete_insurance_from_doc(insurance:DoctorInsurance):
    return delete_insurance_from_doctor(insurance)

@router.get('/doctor/all_doctors/{insurance_id}')
def get_all_docs_of_insurance(insurance_id:int):
    return get_all_doctors_of_insurance(insurance_id)

@router.get('/doctor/all_insurances_of_all_doctors')
def get_all_insurances_docs():
    return get_all_insurances_of_doctors()
