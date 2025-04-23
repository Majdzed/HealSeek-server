from jwt import PyJWTError as JWTError
from fastapi import Request, HTTPException, Depends
from app.database.database import User as us, db
from app.utils.auth import verify_token
from app.enums.roles import Roles

def verify_jwt(request: Request,allowed_roles: list = None):
    try:
        # Extract the Authorization header
        access_token = request.headers.get("Authorization") or request.headers.get("authorization")
        print(request.headers)
        print(access_token)
        if not access_token:
            raise HTTPException(status_code=401, detail="Unauthenticated: Token missing")

        # Ensure token follows the "Bearer <token>" format
        if not access_token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token format")

        # Extract the token part
        access_token = access_token.split(' ')[1]

        # Verify the token using the utility function
        payload = verify_token(access_token)
        print(payload)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Extract user details from the payload
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # Retrieve the user from the database
        user_query = us.find(email=email)
        db.execute_query(user_query, params=(email,))
        user_found = db.fetch_one()

        if not user_found:
            raise HTTPException(status_code=401, detail="User not found")

        # Map database result to a dictionary
        user = {
            "user_id": user_found[0],
            "name": user_found[1],
            "email": user_found[3],
            "role": user_found[9]
        }

        # Role verification
        if allowed_roles:
            # Convert allowed_roles to a list if it's not already
            if isinstance(allowed_roles, str):
                allowed_roles = [allowed_roles]
            elif isinstance(allowed_roles, Roles):
                allowed_roles = [allowed_roles.value]

            # Check if the user's role matches any of the allowed roles
            if user["role"] not in allowed_roles:
                raise HTTPException(status_code=403, detail="Forbidden: Insufficient role")
            request.state.user = user.get("user_id")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Token verification failed")
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error in verify_jwt: {e}")
        raise HTTPException(status_code=500, detail={"message": "Internal Server Error", "exception": str(e)})

def verify_jwt_temp(access_token: str, allowed_roles: list = None):
    try:
        # Verify the token using the utility function
        payload = verify_token(access_token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Extract user details from the payload
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # Retrieve the user from the database
        user_query = us.find(email=email)
        db.execute_query(user_query, params=(email,))
        user_found = db.fetch_one()

        if not user_found:
            raise HTTPException(status_code=401, detail="User not found")

        # Map database result to a dictionary
        user = {
            "user_id": user_found[0],
            "name": user_found[1],
            "email": user_found[3],
            "role": user_found[9]
        }

        # Role verification
        if allowed_roles:
            # Convert allowed_roles to a list if it's not already
            if isinstance(allowed_roles, str):
                allowed_roles = [allowed_roles]
            elif isinstance(allowed_roles, Roles):
                allowed_roles = [allowed_roles.value]

            # Check if the user's role matches any of the allowed roles
            if user["role"] not in allowed_roles:
                raise HTTPException(status_code=403, detail="Forbidden: Insufficient role")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Token verification failed")
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error in verify_jwt: {e}")
        raise HTTPException(status_code=500, detail={"message": "Internal Server Error", "exception": str(e)})