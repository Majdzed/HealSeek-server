from fastapi import APIRouter
router = APIRouter(
    prefix="/review",
    tags=["review"],
)


@router.get("/")
def get_reviews():
    return {"reviews": "reviews"}

@router.get("/{review_id}")
def get_review(review_id: int):
    return {"review_id": review_id}

@router.post("/")
def create_review():
    return {"message": "review created"}

@router.put("/{review_id}")
def update_review(review_id: int):
    return {"message": "review updated"}

@router.delete("/{review_id}")
def delete_review(review_id: int):
    return {"message": "review deleted"}