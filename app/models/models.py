from enum import Enum
from pydoc import Doc
from pydantic import BaseModel, Field
from typing import Optional,List
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid objectid')
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type='string')


class RoleEnum(str, Enum):
    Admin = "admin"
    Doctor = "docteur"
    User = "utilisateur"
    
class GenderEnum(str, Enum):
    Male='homme'
    Female='femme'
    
class CommonBaseModel(BaseModel):
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    

class User(CommonBaseModel):
    email: str
    firstname: Optional[str] = ""
    lastname: Optional[str] = ""
    phone_number: str | None = ""
    date_of_birth: str
    address: str
    Gender: GenderEnum
    username: str
    password: str
    role: RoleEnum = RoleEnum.User
    refreshToken: str = ""
    