from email import message
from app.config import settings
from datetime import datetime,timedelta
import jwt

def sign_access_token(params,type:str):
    payload = params.copy()
    if type == 'access':
        expire = datetime.now() + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRES_IN)
    else:
        expire = datetime.now() + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRES_IN)
    payload.update({"exp":expire})
    print(payload)
    token = jwt.encode(payload, settings.JWT_PRIVATE_KEY, algorithm=settings.JWT_ALGORITHM)
    return token

def verify_token(token :str):
    try:
        payload = jwt.decode(token,settings.JWT_PRIVATE_KEY, algorithms=settings.JWT_ALGORITHM)
        print(payload)
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return {"message":"invalid token"}