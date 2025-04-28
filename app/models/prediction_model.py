# app/models/prediction_model.py

from pydantic import BaseModel
from datetime import datetime

class PredictionBase(BaseModel):
    patient_id: str
    predicted_risk: str  # "low", "medium", "high"
    confidence: float
    model_used: str

class PredictionCreate(PredictionBase):
    pass

class PredictionOut(PredictionBase):
    id: str
    predicted_at: datetime

    class Config:
        orm_mode = True

