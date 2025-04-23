from fastapi import APIRouter
router = APIRouter(
    prefix="/appointment",
    tags=["appointment"],
)


@router.get("/")
def get_appointment():
    return {"appointment": "appointment"}

@router.get("/{appointment_id}")
def get_appointment(appointment_id: int):
    return {"appointment_id": appointment_id}

@router.post("/")
def create_appointment():
    return {"message": "appointment created"}

@router.put("/{appointment_id}")
def update_appointment(appointment_id: int):
    return {"message": "appointment updated"}

@router.delete("/{appointment_id}")
def delete_appointment(appointment_id: int):
    return {"message": "appointment deleted"}