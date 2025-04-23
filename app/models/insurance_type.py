from pydantic import BaseModel

class Insurance(BaseModel):
    type_name : str
    
class DoctorInsurance(BaseModel):
    doctor_id: int
    insurance_type_id: int
    
class DoctorInsurance2(BaseModel):
    doctor_id: int
    insurance_type_name: str