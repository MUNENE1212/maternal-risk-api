# app/routers/alert_router.py
from fastapi import APIRouter, HTTPException
from app.models.alert_model import AlertCreate, AlertOut
from app.db.database import alerts_collection
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.post("/", response_model=AlertOut)
async def create_alert(alert: AlertCreate):
    data = alert.dict()
    data["created_at"] = datetime.utcnow()
    result = await alerts_collection.insert_one(data)
    data["id"] = str(result.inserted_id)
    return AlertOut(**data)

@router.get("/{mother_id}", response_model=list[AlertOut])
async def get_alerts(mother_id: int):
    alerts = await alerts_collection.find({"mother_id": mother_id}).to_list(100)
    return [AlertOut(id=str(a["_id"]), **{k: a[k] for k in a if k != "_id"}) for a in alerts]
