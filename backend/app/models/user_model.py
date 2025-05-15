# app/models/user_model.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str  # e.g., "admin", "health_worker", "analyst"

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True

