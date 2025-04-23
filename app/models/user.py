from pydantic import BaseModel, Field
from app.enums.roles import Roles
from typing_extensions import Annotated
from datetime import datetime, time, timedelta,date
from typing import Optional


mail_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

class User(BaseModel) : 
    name : str
    email: Annotated[str, Field(pattern=mail_regex)] = 'exmp@mail.com'
    password : str
    phone_number : str = Field(default='0666666666')
    date_of_birth: str = Field(default="2000-01-01")
    role: str = Field(default="patient")
    pfpUrl : str
    gender : str 
    
    
class Registration_input(User):
    speciality: Optional[str] = None
    experience: Optional[int] = None
    max_appointments_in_day: Optional[int] = None
    appointment_duration_minutes: Optional[int] = Field(default=30)
    teleconsultation_available: Optional[bool] = None
    office_location: Optional[str] = None
    office_location_url: Optional[str] = None

class Login_input(BaseModel):
    email : str  = Field(default="exmp@mail.com")
    password : str
    
    