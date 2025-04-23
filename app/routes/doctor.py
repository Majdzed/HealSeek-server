from fastapi import APIRouter
router = APIRouter(
    prefix="/doctor",
    tags=["doctor"],
)


@router.get("/")
def get_doctors():
    return {"doctors": "doctor"}

@router.get("/{doctor_id}")
def get_user(doctor_id: int):
    return {"doctor_id": doctor_id}

@router.get("/")
def search_doctor(name: str=''):
    return {"message": name}

@router.post("/")
def create_doctor():
    return {"message": "doctor created"}

@router.put("/{doctor_id}")
def update_user(doctor_id: int):
    return {"message": "doctor updated"}

@router.delete("/{doctor_id}")
def delete_user(doctor_id: int):
    return {"message": "doctor deleted"}
