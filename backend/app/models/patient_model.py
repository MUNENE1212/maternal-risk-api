
# app/models/patient_model.py

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class VitalsEntry(BaseModel):
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    Age: int
    SystolicBP: int
    DiastolicBP: int
    BS: float
    BodyTemp: float
    HeartRate: int
    source: Optional[str] = "manual"  # or "ussd", "web", etc.


class PredictionEntry(BaseModel):
    risk: str
    confidence: float
    model_used: str
    predicted_at: datetime
    input: Optional[VitalsEntry] = None  # ✅ flexible nested model



class PatientBase(BaseModel):
    national_id: str
    full_name: Optional[str] = None
    phone_primary: Optional[str] = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    full_name: Optional[str]
    phone_primary: Optional[str]


class PatientOut(BaseModel):
    id: str
    national_id: str
    full_name: str
    phone_primary: str
    prediction_history: List[PredictionEntry] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # replaces `orm_mode` in Pydantic v2

