# app/models/antenatal_model.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class AntenatalVisitBase(BaseModel):
    pregnancy_id: str
    visit_date: datetime
    visit_number: int
    visit_type: Optional[str] = None  # Facility, Outreach, etc.
    blood_pressure: Optional[str] = None  # Format: systolic/diastolic
    hemoglobin_level: Optional[float] = None
    weight: Optional[float] = None
    bmi: Optional[float] = None
    muac: Optional[float] = None  # Mid-Upper Arm Circumference
    fetal_heart_rate: Optional[int] = None
    fundal_height: Optional[float] = None
    fetal_position: Optional[str] = None
    ultrasound_findings: Optional[dict] = {}
    tetanus_vaccination: Optional[bool] = None
    iron_folate_given: Optional[bool] = None
    malaria_prophylaxis_given: Optional[bool] = None
    deworming_done: Optional[bool] = None
    hiv_status: Optional[str] = None
    malaria_status: Optional[str] = None
    tb_screening: Optional[str] = None
    symptoms: Optional[List[str]] = []
    danger_signs: Optional[List[str]] = []
    medications_prescribed: Optional[List[str]] = []
    nutritional_advice: Optional[str] = None
    next_appointment: Optional[datetime] = None
    referral_needed: Optional[bool] = None
    referral_reason: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[str] = None

class AntenatalVisitCreate(AntenatalVisitBase):
    pass

class AntenatalVisitOut(AntenatalVisitBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True




