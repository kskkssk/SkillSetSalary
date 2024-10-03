import time
from dotenv import load_dotenv
from datetime import datetime
from jose import jwt, JWTError
import os
from fastapi import HTTPException, status

dotenv_path = '/.env'

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')


def create_access_token(user: str) -> str:
    payload = {
        'user': user,
        'expires': time.time() + 3600
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def verify_access_token(token: str) -> dict:
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        expire = data.get("expires")
        if expire is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Token does not exist')
        if datetime.utcnow() > datetime.utcfromtimestamp(expire):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Token expired!')
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid token')