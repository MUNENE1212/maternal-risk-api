# app/models/user_model.py

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Literal, Optional

class UserCreate(BaseModel):
    full_name: str
    phone_number: str  # Use this instead of email
    password: str
    role: str

class UserLogin(BaseModel):
    phone_number: str
    password: str

class UserOut(BaseModel):
    id: str
    full_name: str
    phone_number: str
    role: str

