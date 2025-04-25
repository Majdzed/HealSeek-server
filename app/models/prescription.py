from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class MedicationCreate(BaseModel):
    medication_name: str
    dosage: str
    frequency: str
    duration: str
    instructions: str

class PrescriptionCreate(BaseModel):
    appointment_id: int
    patient_id: int
    diagnosis: str
    notes: str
    medications: List[MedicationCreate]
    doctor_id: Optional[int] = None

class PrescriptionUpdate(BaseModel):
    diagnosis: Optional[str] = None
    notes: Optional[str] = None

class MedicationResponse(BaseModel):
    medication_id: int
    medication_name: str
    dosage: str
    frequency: str
    duration: str
    instructions: str

class PrescriptionResponse(BaseModel):
    prescription_id: int
    appointment_id: int
    doctor_id: int
    patient_id: int
    diagnosis: str
    notes: str
    created_at: datetime
    updated_at: datetime
    medications: List[MedicationResponse]