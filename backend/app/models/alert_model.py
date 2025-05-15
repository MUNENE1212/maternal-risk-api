# app/models/alert_model.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AlertBase(BaseModel):
    mother_id: int
    pregnancy_id: str
    alert_type: str  # SMS, App, Emergency
    alert_priority: str  # Normal, Urgent, Emergency
    message: str
    language: Optional[str] = "English"
    delivered: Optional[bool] = False
    read: Optional[bool] = False
    response_received: Optional[bool] = False
    response_content: Optional[str] = None

class AlertCreate(AlertBase):
    pass

class AlertOut(AlertBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True
