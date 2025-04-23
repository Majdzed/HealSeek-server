from fastapi import APIRouter, HTTPException, Cookie, File, UploadFile, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.user import Registration_input, Login_input
from app.controllers.auth_conrtollers import registeration, login as auth_login, logout as auth_logout, handle_refresh_token, verify_2fa
from app.utils.twoFA import generate_2fa_code, verify_2fa_code
from app.utils.auth import verify_token
from fastapi import Response, Request, status
from fastapi.responses import JSONResponse
from app.routes.user_routes import resolve_user_temp

router = APIRouter()

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload

@router.post('/register', description="Register a new user in the system.", response_description="Returns the registered user data.")
async def register_user(User: Registration_input):
    response = await registeration(User)
    return response

@router.post("/login", description="Authenticate a user and generate access tokens.", response_description="Returns an access token or a 2FA request.")
def login(user_credentials: Login_input, response: Response):
    response = auth_login(user_credentials, response)
    return response

@router.get("/logout", description="Log out a user by invalidating their refresh token.", response_description="Returns a message indicating logout status.")
def logout(response: Response, request: Request,current_user: dict = Depends(get_current_user) ):
    response = auth_logout(response, request)
    return response

@router.get("/refresh", description="Handle refresh token to generate new access token.", response_description="Returns a new access token.")
def refresh_token(response: Response, request: Request,current_user: dict = Depends(get_current_user)):
    response = handle_refresh_token(response, request)
    return response

@router.post("/2fa", description="Verify 2FA code and complete login process.", response_description="Returns an access token.")
def verify_2fa_code(code: str, request: Request):
    return verify_2fa(code, request)

@router.get("/protected/user", description="Protected route for users only.", response_description="Returns user-specific data.")
async def protected_user_route(current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin", "patient", "doctor"]))):
    return {
        "message": "You have accessed a user protected route",
        "user": current_user,
        "role": "user"
    }

@router.get("/protected/doctor", description="Protected route for doctors only.", response_description="Returns doctor-specific data.")
async def protected_doctor_route(current_user: dict = Depends(resolve_user_temp(allowed_roles=["doctor"]))):
    return {
        "message": "You have accessed a doctor protected route",
        "user": current_user,
        "role": "doctor"
    }

@router.get("/protected/patient", description="Protected route for patients only.", response_description="Returns patient-specific data.")
async def protected_patient_route(current_user: dict = Depends(resolve_user_temp(allowed_roles=["patient"]))):
    return {
        "message": "You have accessed a patient protected route",
        "user": current_user,
        "role": "patient"
    }

@router.get("/protected/admin", description="Protected route for administrators only.", response_description="Returns admin-specific data.")
async def protected_admin_route(current_user: dict = Depends(resolve_user_temp(allowed_roles=["admin"]))):
    return {
        "message": "You have accessed an admin protected route",
        "user": current_user,
        "role": "admin"
    }