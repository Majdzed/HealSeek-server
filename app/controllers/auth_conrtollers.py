from datetime import datetime ,timedelta , timezone
from email import message
from enum import Enum
from typing import Annotated
from uuid import uuid4
import json
import jwt
import asyncio
from fastapi import HTTPException, Request, Response, Form, Cookie
from fastapi.responses import JSONResponse, RedirectResponse
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from app.utils.auth import sign_access_token, verify_token
from app.utils.twoFA import generate_2fa_code, verify_2fa_code
from app.database.database import User as us, db, Doctor, Patient, Admin
from app.enums.roles import Roles
from app.models.user import Registration_input, Login_input
from passlib.hash import bcrypt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
ph = PasswordHasher()


class UserRole(str, Enum):
    """Enum for user roles in the system."""
    DOCTOR = "doctor"
    PATIENT = "patient"
    ADMIN = "admin"

async def check_email(user, db):
    user_query_email = us.find(email=user["email"])
    db.execute_query(user_query_email, params=(user["email"],))
    return db.fetch_one()

async def check_phone_number(user, db):
    user_query_phone_number = us.find(phone_number=user["phone_number"])
    db.execute_query(user_query_phone_number, params=(user["phone_number"],))
    return db.fetch_one()


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2.

    Args:
        password (str): The plaintext password to hash.

    Returns:
        str: The hashed password.
    """
    try:
        # Hash the password
        hashed_password = ph.hash(password)
        return hashed_password
    except Exception as e:
        # Log the error and raise an exception
        logger.error(f"Password hashing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing password")

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hashed version.

    Args:
        password (str): The plaintext password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    try:
        # Verify the password
        return ph.verify(hashed_password, password)
    except VerifyMismatchError:
        # Password does not match
        return False
    except Exception as e:
        # Log the error and raise an exception
        logger.error(f"Password verification failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Error verifying password")

async def registeration(User: Registration_input) -> Response:
    """
    Register a new user in the system with transaction support.
    
    Args:
        User (Registration_input): User registration data
        
    Returns:
        Response: JSON response with registration status and user ID
        
    Raises:
        HTTPException: 
            - 400: Validation fails or user exists
            - 500: Database operation fails
    """
    user = dict(User)

    # Validate required fields
    required_fields = {
        'password': 'Password is required',
        'email': 'Email is required',
        'name': 'Name is required',
        'role': 'Role is required'
    }
    # if user["role"] == "admin":
    #     raise HTTPException(
    #     status_code=403,
    #     detail="Admin registration is not allowed"
    #     )

    for field, message in required_fields.items():
        if not user.get(field):
            raise HTTPException(status_code=400, detail=message)

    # Validate and normalize role
    try:
        role = UserRole(user["role"].lower())
        user["role"] = role.value
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid role. Must be one of: {', '.join([r.value for r in UserRole])}"
        )

    # Process date of birth if provided
    if user.get("date_of_birth"):
        try:
            date_obj = datetime.strptime(user["date_of_birth"], '%Y-%m-%d')
            user["date_of_birth"] = date_obj.strftime('%Y-%m-%d')
        except ValueError as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid date format for date_of_birth. Use YYYY-MM-DD: {str(e)}"
            )

    # Validate unique email and phone number
    try:
        email_exists, phone_exists = await asyncio.gather(
            check_email(user, db),
            check_phone_number(user, db) if user.get("phone_number") else None
        )
        
        if email_exists:
            raise HTTPException(status_code=400, detail="Email already exists")
        if phone_exists:
            raise HTTPException(status_code=400, detail="Phone number already exists")
    except Exception as e:
        logger.error(f"Error checking user credentials: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Error validating user information"
        )

    # Hash password


    try:
        # Hash the password
        user["password"] = hash_password(user["password"])
    except Exception as e:
        # Log the error and raise an exception
        logger.error(f"Password hashing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing password")

    # Generate user ID
    userId = int(''.join(filter(str.isdigit, str(uuid4())))[:6])

    try:
        with db.transaction():
            # Create base user
            db.execute_query(us.create(
                user_id=userId,
                Name=user['name'],
                Email=user["email"].lower(),
                PhoneNumber=user.get("phone_number"),
                DateOfBirth=user.get("date_of_birth"),
                Password=user["password"],
                role=user["role"],
                gender=user.get("gender"),
                profile_picture_url=user.get("pfpUrl")
            ))

            # Create role-specific profile
            if user['role'] == "doctor":
                if not all(k in user for k in ['speciality', 'experience', 'max_appointments_in_day', 
                                            'appointment_duration_minutes']):
                    raise HTTPException(status_code=400, detail="Missing required doctor information")
                    
                db.execute_query(Doctor.create(
                    user_id=userId,
                    speciality=user['speciality'],
                    experience=user['experience'],
                    max_appointments_in_day=user['max_appointments_in_day'],
                    appointment_duration_minutes=user['appointment_duration_minutes'],
                    teleconsultation_available=user.get('teleconsultation_available', False),
                    office_location=user.get('office_location'),
                    office_location_url=user.get('office_location_url')
                ))
            
            elif user['role'] == "patient":
                db.execute_query(Patient.create(user_id=userId))
            
            elif user['role'] == "admin":
                db.execute_query(Admin.create(
                    user_id=userId,
                    two_factor_auth_enabled=True,
                    last_login=datetime.now().isoformat()
                ))

        return Response(
            content=json.dumps({
                "message": "Registration successful",
                "user_id": userId
            }),
            media_type="application/json",
            status_code=201
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed for {user.get('email')}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Registration failed",
                "error": str(e)
            }
        )
def login(userCredentials: Login_input, response: Response) -> JSONResponse:
    """
    Authenticate a user and generate access tokens.
    
    Args:
        userCredentials (Login_input): User login credentials
        response (Response): FastAPI response object
        
    Returns:
        JSONResponse: Response with access token or 2FA request
        
    Raises:
        HTTPException: 400 if credentials are invalid
    """
    userCredentials = dict(userCredentials)
    email = userCredentials["email"].lower()
    password = userCredentials["password"]

    # Find user
    user_query = us.find(email=email)
    db.execute_query(user_query, params=(email,))
    user_found = db.fetch_one()
    
    if not user_found:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    user_found = {
        "password": user_found[6],
        "email": user_found[3],
        "role": user_found[9],
        "user_id": user_found[0]
    }

    #Verify password

    if not verify_password(password,user_found["password"]):
        raise HTTPException(status_code=400, detail="Wrong password")

    # Generate tokens
    access_token = sign_access_token({"email": user_found["email"], "role": user_found["role"]}, 'access')
    refresh_token = sign_access_token({"email": user_found["email"], "role": user_found["role"]}, 'refresh')
    
    # Update refresh token in database
    logged_user_query = us.update(refresh_token=refresh_token, user_id=user_found["user_id"])
    db.execute_query(logged_user_query, params=(refresh_token, user_found["user_id"]))

    # Handle admin 2FA
    if user_found["role"] == "admin":
        found_admin = Admin.find(user_id=user_found["user_id"])
        db.execute_query(found_admin, params=(user_found["user_id"],))
        found_admin = db.fetch_one()
        
        if found_admin[1]:  # If 2FA is enabled
            generate_2fa_code(receiver=user_found["email"])
            temp_2fa_token = sign_access_token(
                {"email": user_found["email"], "user_id": user_found["user_id"]},
                "2fa"
            )
            return JSONResponse(
                content={"message": "2FA code sent to your email."},
                status_code=200,
                headers={"Set-Cookie": f"temp_2fa_token={temp_2fa_token}; HttpOnly; Max-Age=300; SameSite=None ;"}
            )

        # Update admin last login
        Admin_query = Admin.update(last_login=datetime.now().isoformat(), user_id=user_found["user_id"])
        db.execute_query(Admin_query, params=(datetime.now().isoformat(), user_found["user_id"]))

    response =  JSONResponse(
        content={"accessToken": access_token},
        status_code=200,
    )

    secure_flag = True
    
    response.set_cookie(
        key="jwt",
        value=refresh_token,
        max_age=7 * 24 * 60 * 60,
        expires=(datetime.utcnow() + timedelta(days=7)).replace(tzinfo=timezone.utc),
        path="/",
        secure=True,  # Required for cross-site cookies
        httponly=True,
        samesite="None"  # Must be "None" for cross-site cookies
    )

    return response

def logout(response: Response, request: Request) -> dict:
    """
    Log out a user by invalidating their refresh token.
    
    Args:
        response (Response): FastAPI response object
        request (Request): FastAPI request object
        
    Returns:
        dict: Message indicating logout status
    """
    cookies = request.cookies.get("jwt")
    if not cookies:
        return {"message": "Already logged out"}

    user = us.find(refresh_token=cookies)
    db.execute_query(user, params=(cookies,))
    user_data = db.fetch_one()
    
    if not user_data:
        response.delete_cookie('jwt' , path='/')
        return {"message": "No active session found"}
    
    # Clear refresh token
    logged_user_query = us.update(refresh_token="", user_id=user_data[0])
    db.execute_query(logged_user_query, params=("", user_data[0]))
    response.delete_cookie('jwt', path="/")
    return {"message": "User has been logged out"}

def handle_refresh_token(response: Response, request: Request) -> dict:
    """
    Handle refresh token to generate new access token.
    
    Args:
        response (Response): FastAPI response object
        request (Request): FastAPI request object
        
    Returns:
        dict: New access token
        
    Raises:
        HTTPException: 403 if token is invalid
                      500 if token verification fails
    """
    print("hna ntestiz")
    cookies = request.cookies.get("jwt")
    print(cookies)
    if not cookies:
        return {"no token provided"}

    try:
        user = us.find(refresh_token=cookies)
        db.execute_query(user, params=(cookies,))
        user = db.fetch_one()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while finding user")

    if not user:
        raise HTTPException(status_code=403, detail="Access forbidden")

    user = {"email": user[3], "role": user[9]}
    try:
        payload = verify_token(cookies)
        if payload["email"] != user["email"]:
            return {"message": "invalid token"}
        access_token = sign_access_token({"email": user["email"], "role": user["role"]}, 'access')
        return {"accessToken": access_token}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while verifying token")

def verify_2fa(code: str, request: Request) -> JSONResponse:
    """
    Verify 2FA code and complete login process.
    
    Args:
        code (str): 2FA code to verify
        request (Request): FastAPI request object
        
    Returns:
        JSONResponse: Response with access token
        
    Raises:
        HTTPException: 400 if 2FA verification fails
    """
    temp_2fa_token = request.cookies.get("temp_2fa_token")
    if not temp_2fa_token:
        raise HTTPException(status_code=400, detail="2FA session expired or invalid.")
    
    try:
        payload = verify_token(temp_2fa_token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired 2FA token.")
    
    if not verify_2fa_code(code):
        raise HTTPException(status_code=400, detail="Invalid 2FA code.")

    # Generate final tokens
    access_token = sign_access_token({"email": payload["email"], "role": "admin"}, "access")
    refresh_token = sign_access_token({"email": payload["email"], "role": "admin"}, "refresh")

    return JSONResponse(
        content={"accessToken": access_token},
        status_code=200,
        headers={"Set-Cookie": f"jwt={refresh_token}; HttpOnly; Max-Age=1800; SameSite=Lax"}
    )