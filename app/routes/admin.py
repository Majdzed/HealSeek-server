from fastapi import APIRouter
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


@router.get("/")
def get_users():
    return {"users": "users"}

@router.get("/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}

@router.post("/")
def create_user():
    return {"message": "user created"}

@router.put("/{user_id}")
def update_user(user_id: int):
    return {"message": "user updated"}

@router.delete("/{user_id}")
def delete_user(user_id: int):
    return {"message": "user deleted"}

@router.post("block/{user_id}")
def block_user(user_id: int):
    return {"message": "user blocked"}

@router.post("unblock/{user_id}")
def unblock_user(user_id: int):
    return {"message": "user unblocked"}

@router.post("delete_review/{review_id}")
def delete_innapropriate_review(review_id: int):
    return {"message": "review deleted"}