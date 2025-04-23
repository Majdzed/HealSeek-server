from fastapi import APIRouter
router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.get("/")
def get_users():
    return {"users": "users"}

@router.get("/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}

@router.get("/{patient_id}/history")
def get_patient_history(patient_id: int):
    return {"message": "patient history"}

@router.post("/")
def create_user():
    return {"message": "user created"}

@router.put("/{user_id}")
def update_user(user_id: int):
    return {"message": "user updated"}

@router.delete("/{user_id}")
def delete_user(user_id: int):
    return {"message": "user deleted"}
@router.post("/book_appointment")
def book_appointment():
    return {"message": "appointment booked"}
