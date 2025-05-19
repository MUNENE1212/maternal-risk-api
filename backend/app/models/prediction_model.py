# app/models/prediction_model.py

from pydantic import BaseModel
from datetime import datetime

class PredictionBase(BaseModel):
    national_id: str
    risk: str  # "low", "medium", "high"
    confidence: float
    model_used: str
    predicted_at:datetime

class PredictionCreate(PredictionBase):
    pass

class PredictionOut(PredictionBase):
    id: national_id
    predicted_at: datetime

    class Config:
        orm_mode = True

