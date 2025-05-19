# app/routers/patient_router.py

from fastapi import APIRouter, HTTPException, status, Depends, Request
from bson import ObjectId
from app.middleware.rbac import require_role
from app.models.patient_model import PatientCreate, PatientOut
from app.db.database import patients_collection
from datetime import datetime
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/patients", tags=["Patients"])

def patient_helper(patient) -> dict:
    from datetime import datetime

    def normalize_prediction(entry):
        default_input = {
            "Age": 0,
            "SystolicBP": 0,
            "DiastolicBP": 0,
            "BS": 0.0,
            "BodyTemp": 0.0,
            "HeartRate": 0
        }

        input_data = {**default_input, **entry.get("input", {})}

        return {
            "risk": entry.get("risk", entry.get("predicted_risk", "")),
            "confidence": entry.get("confidence", 0.0),
            "model_used": entry.get("model_used", "unknown"),
            "predicted_at": entry.get("predicted_at", datetime.utcnow()),
            "input": input_data
        }

    # Safely normalize prediction history
    raw_history = patient.get("prediction_history", [])
    normalized_history = [normalize_prediction(entry) for entry in raw_history if entry]

    return {
        "id": str(patient["_id"]),
        "national_id": str(patient["_id"]),  # Changed from national_id to nationalId
        "full_name": patient.get("full_name", ""),  # camelCase
        "phone_primary": patient.get("phone_primary", ""),
        "vitals_history": patient.get("vitals_history", []),
        "prediction_history": normalized_history,
        "created_at": patient.get("created_at", datetime.utcnow()),
        "updated_at": patient.get("updated_at", datetime.utcnow())
    }





# 🟢 Add Patient with custom _id
@router.post("/", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
async def add_patient(patient: PatientCreate):
    # Check if patient already exists
    existing = await patients_collection.find_one({"_id": patient.national_id})
    if existing:
        raise HTTPException(status_code=409, detail="Patient with this ID already exists.")

    patient_data = patient.dict()
    patient_data["vitals_history"] = []
    patient_data["prediction_history"] = []
    patient_data["created_at"] = datetime.utcnow()
    patient_data["updated_at"] = datetime.utcnow()
    patient_data["_id"] = patient_data.pop("national_id")  # use ID number as _id
    patient_data["submitted_by"] = "user_001"  # Replace with real user from token
    patient_data["submitted_at"] = datetime.utcnow()

    await patients_collection.insert_one(patient_data)
    return patient_helper(patient_data)

# 🔵 Get All Patients
@router.get("/", response_model=list[PatientOut])
async def get_all_patients():
    patients = []
    async for patient in patients_collection.find():
        try:
            print("Processing:", patient)
            patients.append(patient_helper(patient))
        except Exception as e:
            print("Error processing patient:", e)
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


@router.get("/dashboard", response_class=HTMLResponse)
async def patient_dashboard(request: Request, user=Depends(require_role(["patient"]))):
    return templates.TemplateResponse("mother_dashboard.html", {"request": request, "user": user})
