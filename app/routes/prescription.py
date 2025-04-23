from fastapi import APIRouter
router = APIRouter(
    prefix="/prescription",
    tags=["prescription"],
)


@router.get("/")
def get_prescription():
    return {"prescription": "prescriptions"}

@router.get("/{prescription_id}")
def get_prescription(prescription_id: int):
    return {"prescription_id": prescription_id}

@router.post("/")
def create_prescription():
    return {"message": "prescription created"}

@router.put("/{prescription_id}")
def update_prescription(prescription_id: int):
    return {"message": "prescription updated"}

@router.delete("/{prescription_id}")
def delete_prescription(prescription_id: int):
    return {"message": "prescription deleted"}