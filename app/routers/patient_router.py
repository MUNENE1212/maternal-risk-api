# app/routers/patient_router.py

from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from app.models.patient_model import PatientCreate, PatientOut
from app.db.database import patients_collection
from datetime import datetime

router = APIRouter(prefix="/patients", tags=["Patients"])

# 🧠 Convert document to response dict
def patient_helper(patient) -> dict:
    return {
        "id": patient["_id"],  # now equals id_number
        "full_name": patient["full_name"],
        "id_number": patient["_id"],
        "age": patient["age"],
        "pregnancies": patient["pregnancies"],
        "systolic_bp": patient["systolic_bp"],
        "diastolic_bp": patient["diastolic_bp"],
        "bmi": patient["bmi"],
        "glucose": patient["glucose"],
        "submitted_by": str(patient["submitted_by"]),
        "submitted_at": patient["submitted_at"]
    }

# 🟢 Add Patient with custom _id
@router.post("/", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
async def add_patient(patient: PatientCreate):
    # Check if patient already exists
    existing = await patients_collection.find_one({"_id": patient.id_number})
    if existing:
        raise HTTPException(status_code=409, detail="Patient with this ID already exists.")

    patient_data = patient.dict()
    patient_data["_id"] = patient_data.pop("id_number")  # use ID number as _id
    patient_data["submitted_by"] = "user_001"  # Replace with real user from token
    patient_data["submitted_at"] = datetime.utcnow()

    await patients_collection.insert_one(patient_data)
    return patient_helper(patient_data)

# 🔵 Get All Patients
@router.get("/", response_model=list[PatientOut])
async def get_all_patients():
    patients = []
    async for patient in patients_collection.find():
        patients.append(patient_helper(patient))
    return patients

# 🟣 Get One by ID
@router.get("/{id}", response_model=PatientOut)
async def get_patient(id: str):
    patient = await patients_collection.find_one({"_id": id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient_helper(patient)

# 🔴 Delete by ID
@router.delete("/{id}")
async def delete_patient(id: str):
    result = await patients_collection.delete_one({"_id": id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deleted successfully"}

