
# app/models/patient_model.py

from pydantic import BaseModel, Field
from datetime import datetime

class PatientBase(BaseModel):
    full_name: str
    id_number: str  # Used as custom MongoDB _id
    age: int
    pregnancies: int
    systolic_bp: float
    diastolic_bp: float
    bmi: float
    glucose: float
    

class PatientCreate(PatientBase):
    pass

class PatientOut(PatientBase):
    id: str  # same as id_number
    submitted_by: str
    submitted_at: datetime

    class Config:
        orm_mode = True

