from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import time, datetime

class AvailabilityBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: time
    end_time: time
    is_available: bool = True

    @validator('start_time', 'end_time')
    def validate_times(cls, v):
        return v

    @validator('end_time')
    def validate_time_range(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

class TimeOffBase(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
    reason: Optional[str] = None

    @validator('end_datetime')
    def validate_datetime_range(cls, v, values):
        if 'start_datetime' in values and v <= values['start_datetime']:
            raise ValueError('end_datetime must be after start_datetime')
        return v

class LanguageBase(BaseModel):
    language_id: int

class InsuranceBase(BaseModel):
    insurance_type_id: int