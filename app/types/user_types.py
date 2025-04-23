from pydantic import BaseModel
from app.models.models import GenderEnum, RoleEnum
class login_input(BaseModel):
    username: str
    email: str
    password: str
    
class register_input(BaseModel):
    username: str
    email: str
    password: str
    confirm_password:str
    firstname: str
    lastname: str
    phone_number: str | None = ""
    date_of_birth: str
    address: str
    Gender: GenderEnum
    role: RoleEnum = RoleEnum.User