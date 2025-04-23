from re import U
from fastapi import HTTPException, Request, Response
from app.database import User
from app.types.user_types import login_input, register_input
from app.models.models import User as UserModel
from app.utils.auth import sign_token, verify_token
import bcrypt

def login(userCredentials : login_input,response:Response):
    username = userCredentials.username
    email = userCredentials.email
    password = userCredentials.password
    try:
        username_found = User.find_one({"username":username})
        email_found = User.find_one({"email:": email})
        if not username_found and not email_found:
            raise HTTPException(status_code=400, detail="Invalid credentials")
        if username_found:
            if not bcrypt.checkpw(password.encode('utf-8'), username_found["password"].encode('utf-8')):
                
                raise HTTPException(status_code=400, detail="Invalid credentials")
        elif email_found:
            if not bcrypt.checkpw(password.encode('utf-8'),email_found["password"].encode('utf-8')):
                
                raise HTTPException(status_code=400, detail="Invalid credentials")
        
        access_token = sign_token({"sub": username_found["username"],"email": username_found["email"],"role": username_found["role"]},'access')
        refresh_token = sign_token({"sub": username_found["username"],"email": username_found["email"],"role": username_found["role"]},'refresh')
        username_found['refreshToken']=refresh_token
        User.update_one(
            {"_id":username_found["_id"]},
            {"$set": {"refreshToken": refresh_token}}
        )
        response.set_cookie(key='jwt',value=refresh_token,httponly=True,secure=True)
        return {"accessToken":access_token}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def register(userCredentials : register_input):
    user_data = userCredentials.model_dump()
    # to be changed according to the database
    try:
        found_email = User.find_one({"email": user_data["email"]})
        found_user = User.find_one({"username": user_data["username"]})
        if found_user:
            raise HTTPException(status_code=400, detail="username already used")
        if found_email:
            raise HTTPException(status_code=400, detail="email already used")
        if user_data["password"] != user_data["confirm_password"]:
            raise HTTPException(status_code=400, detail="passwords do not match")
        del user_data["confirm_password"]
        hashed_password = bcrypt.hashpw(user_data["password"].encode('utf-8'), bcrypt.gensalt())
        user_data["password"] = hashed_password
        new_user = UserModel(**user_data)

        created = User.insert_one(new_user.model_dump())
        return {"message": "User Created successfully","user": new_user.model_dump()}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
def logout(response:Response,request:Request):
    cookies = request.cookies.get("jwt")
    if not cookies:
        return {"logged out"}
    user = User.find_one({"refreshToken":cookies})
    if not user:
        response.delete_cookie('jwt')
    User.update_one(
        {"_id":user["_id"]},
        {"$set":{"refreshToken":""}})
    response.delete_cookie('jwt')
    return {"message": "User has been logged out"}

def handle_refresh_token(response:Response,request:Request):
    try:
        cookies = request.cookies.get("jwt")
        if not cookies:
            return {"no token provided"}
        user = User.find_one({"refreshToken":cookies})
        if not user:
            raise HTTPException(status_code=403, detail="Access forbidden")
        payload = verify_token(cookies)
        print(payload)
        if payload["sub"] != user["username"]:
            return {"message":"invalid token"}
        access_token = sign_token({"sub": user["username"],"email": user["email"],"role": user["role"]},'access')
        return {"accessToken":access_token}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")