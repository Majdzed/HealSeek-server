from fastapi import APIRouter , HTTPException ,Depends , Request , Path, status
from app.controllers.ratings_controller import get_all_ratings , add_rating , get_rating_by_id , update_rating , delete_rating , get_ratings_by_doctor , get_ratings_by_patient
from app.models.rating import Rating
from app.routes.user_routes import resolve_user_temp
from typing import List, Optional
from pydantic import BaseModel
class RatingResponse(BaseModel):
    id: int
    user_id: int
    doctor_id: int
    rating: int
    review: Optional[str]
    created_at: str

class MessageResponse(BaseModel):
    message: str
    status: str
router = APIRouter()

@router.get(
    "/",
    response_model=List[RatingResponse],
    description="Retrieve all ratings in the system.",
    response_description="Returns a list of all ratings with their details.",
    responses={
        200: {"description": "Successfully retrieved all ratings"},
        404: {"description": "No ratings found"}
    }
)
async def get_all():
    return get_all_ratings()

@router.post(
    "/",
    response_model=RatingResponse,
    description="Add a new rating for a doctor. Only patients can add ratings.",
    response_description="Returns the newly created rating.",
    responses={
        201: {"description": "Rating successfully created"},
        400: {"description": "Invalid rating data"},
        403: {"description": "Only patients can add ratings"}
    },
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(resolve_user_temp(allowed_roles=["patient"]))]
)
async def add(
    request: Request,
    rating: Rating
):
    return add_rating(request, rating=rating)

@router.get(
    "/{rating_id}",
    response_model=RatingResponse,
    description="Retrieve a specific rating by its ID.",
    response_description="Returns the details of the specified rating.",
    responses={
        200: {"description": "Successfully retrieved the rating"},
        404: {"description": "Rating not found"}
    }
)
async def get_by_id(
    rating_id: int = Path(
        ...,
        description="The ID of the rating to retrieve",
        gt=0,
        example=1
    )
):
    return get_rating_by_id(rating_id)

@router.put(
    "/{rating_id}",
    response_model=RatingResponse,
    description="Update an existing rating. Only the patient who created the rating can update it.",
    response_description="Returns the updated rating.",
    responses={
        200: {"description": "Rating successfully updated"},
        400: {"description": "Invalid update data"},
        403: {"description": "Not authorized to update this rating"},
        404: {"description": "Rating not found"}
    },
    dependencies=[Depends(resolve_user_temp(allowed_roles=["patient"]))]
)
async def update(
    request: Request,
    rating_id: int = Path(
        ...,
        description="The ID of the rating to update",
        gt=0,
        example=1
    ),
    rating: dict = None
):
    return update_rating(request, rating_id, rating)

@router.delete(
    "/{rating_id}",
    response_model=MessageResponse,
    description="Delete a rating. Can be done by the patient who created it or an admin.",
    response_description="Returns a success message after deletion.",
    responses={
        200: {
            "description": "Rating successfully deleted",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Rating successfully deleted",
                        "status": "success"
                    }
                }
            }
        },
        403: {"description": "Not authorized to delete this rating"},
        404: {"description": "Rating not found"}
    },
    dependencies=[Depends(resolve_user_temp(allowed_roles=["patient", "admin"]))]
)
async def delete(
    rating_id: int = Path(
        ...,
        description="The ID of the rating to delete",
        gt=0,
        example=1
    )
):
    return delete_rating(rating_id)
@router.get(
    "/doctor/{doctor_id}",
    response_model=List[RatingResponse],
    description="Retrieve all ratings for a specific doctor.",
    response_description="Returns a list of all ratings for the specified doctor.",
    responses={
        200: {"description": "Successfully retrieved doctor's ratings"},
        404: {"description": "No ratings found for this doctor"},
        500: {"description": "Internal server error"}
    }
)
async def get_doctor_ratings(
    doctor_id: int = Path(
        ...,
        description="The ID of the doctor whose ratings to retrieve",
        gt=0,
        example=1
    )
):
    return get_ratings_by_doctor(doctor_id)

@router.get(
    "/patient/{patient_id}",
    response_model=List[RatingResponse],
    description="Retrieve all ratings made by a specific patient.",
    response_description="Returns a list of all ratings made by the specified patient.",
    responses={
        200: {"description": "Successfully retrieved patient's ratings"},
        403: {"description": "Not authorized to view these ratings"},
        404: {"description": "No ratings found for this patient"},
        500: {"description": "Internal server error"}
    },
    dependencies=[Depends(resolve_user_temp(allowed_roles=["patient", "admin"]))]
)
async def get_patient_ratings(
    request: Request,
    patient_id: int = Path(
        ...,
        description="The ID of the patient whose ratings to retrieve",
        gt=0,
        example=1
    )
):
    return get_ratings_by_patient(request, patient_id)