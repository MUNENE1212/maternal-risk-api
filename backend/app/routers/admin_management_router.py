# app/routers/admin_management_router.py
from fastapi import APIRouter, HTTPException, Form
from app.db.database import users_collection
from passlib.hash import bcrypt
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/create-clinician")
async def create_clinician(
    full_name: str = Form(...),
    phone_number: str = Form(...),
    password: str = Form(...)
):
    # Normalize phone
    phone_number = "+254" + phone_number.lstrip("0")
    if await users_collection.find_one({"phone_number": phone_number}):
        raise HTTPException(status_code=400, detail="Clinician with this phone already exists")

    user_data = {
        "full_name": full_name,
        "phone_number": phone_number,
        "password": bcrypt.hash(password),
        "role": "clinician",
        "created_at": datetime.utcnow()
    }
    await users_collection.insert_one(user_data)
    return {"message": "Clinician created successfully"}

