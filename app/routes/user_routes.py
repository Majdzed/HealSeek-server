from fastapi import APIRouter, HTTPException,Query, Request, UploadFile,status, File, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.controllers.user_controllers import (
    get_all_users as get_users,
    update_user,
    get_user_by_id as get_id,
    get_user_by_email as get_email,
    delete_user as delete,
    switch_2fa_status,
    add_admin,
    change_pfp,
)
from typing import Optional
from app.middlewares.verify_jwt import verify_jwt , verify_jwt_temp

router = APIRouter()
security = HTTPBearer()
def resolve_user(allowed_roles: list = None):
    def dependency(request: Request):
        return verify_jwt(request, allowed_roles=allowed_roles)
    return dependency

def resolve_user_temp(allowed_roles: list = None):
    async def dependency(credentials: HTTPAuthorizationCredentials = Depends(security)):
        print("credentials")
        print(credentials)
        try:
            access_token = credentials.credentials
            user = verify_jwt_temp(access_token, allowed_roles=allowed_roles)
            return user
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Internal Server Error",
                    "exception": "403: Forbidden: Insufficient role"
                }
            )
    return dependency
# Routes

@router.get('/', 
    description="Fetch all users with optional filtering by email and name. Admin access only.", 
    response_description="Returns a list of filtered users or all users if no filters applied.",
    responses={
        200: {"description": "Users retrieved successfully"},
        404: {"description": "No users found"},
        500: {"description": "Internal server error"}
    }
)
def get_all_users(
    email: Optional[str] = Query(None, description="Filter users by email (partial match)"),
    name: Optional[str] = Query(None, description="Filter users by name (partial match)"),
    current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin"]))
):
    return get_users(email=email, name=name)

@router.get('/profile', description="Fetch the profile of the current user.", response_description="Returns the user's profile data.")
def get_profile(current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin", "patient", "doctor"]))):
    user_id = current_user["user_id"]
    return get_id(user_id)

@router.get('/{user_id}', description="Fetch user details by user ID.", response_description="Returns the user data.")
def get_user_by_id_route(user_id: int, current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin", "patient", "doctor"]))):
    return get_id(user_id)

@router.put('/{user_id}', description="Update user details the update is with token", response_description="Returns the updated user data.")
def update_user_route(user_data: dict, current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin", "patient", "doctor"]))):
    user_id = current_user["user_id"]
    return update_user(user_id, user_data)

@router.delete('/{user_id}', description="Delete a user by their ID. Admin access only.", response_description="Returns a message indicating the deletion status.")
def delete_user_route(user_id: int, current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin"]))):
    return delete(user_id)



@router.put('/add-admin/{user_id}', description="Promote a user to admin.", response_description="Returns a message indicating the promotion status.")
def add_admin_route(user_id: int, current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin"]))):
    return add_admin(user_id)

@router.put('/switch-2fa', description="Toggle 2FA status for the current user.", response_description="Returns a message indicating the 2FA status change.")
def switch_2fa_route(current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin", "patient", "doctor"]))):
    return switch_2fa_status(user_email=current_user["email"])

@router.put('/change-pfp/{userid}', description="Change profile picture for a specific user.", response_description="Returns a message indicating the profile picture change status.")
def change_pfp_route(file: UploadFile, userid: int, current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin", "patient", "doctor"]))):
    return change_pfp(file, userid)
