from pydantic import BaseModel

class Rating(BaseModel):
    rating_score: int
    review_text: str
    doctor_id: int
    patient_id: int
