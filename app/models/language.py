from pydantic import BaseModel

class Language(BaseModel):
    language_name : str

class DoctorLanguage(BaseModel):
    doctor_id: int
    language_id: int

class DoctorLanguage2(BaseModel):
    doctor_id: int
    language_name: str
