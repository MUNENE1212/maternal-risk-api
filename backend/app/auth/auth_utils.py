# app/utils/auth_utils.py

from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Request, HTTPException, status, Depends
from app.db.database import users_collection
import os

# 🔐 Shared Auth Config
SECRET_KEY = os.getenv("JWT_SECRET", "your_jwt_secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# 🔑 Create JWT Token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 🧠 Get Current User from JWT (Used in RBAC and routes)
async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone = payload.get("sub")  # This is phone_number
        if phone is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = await users_collection.find_one({"phone_number": phone})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token")
