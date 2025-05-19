from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from app.db.database import patients_collection
from app.routers.prediction_router import model, scaler,label_encoder
from app.services.sms_sender import send_sms
import numpy as np

router = APIRouter(prefix="/antenatal", tags=["Antenatal Visits"])

class AntenatalVitals(BaseModel):
    national_id: str
    Age: int
    SystolicBP: int
    DiastolicBP: int
    BS: float
    BodyTemp: float
    HeartRate: int

@router.post("/visit")
async def record_visit(data: AntenatalVitals):
    try:
        patient = await patients_collection.find_one({"national_id": data.national_id})
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        features = np.array([[data.Age, data.SystolicBP, data.DiastolicBP, data.BS, data.BodyTemp, data.HeartRate]])
        scaled = scaler.transform(features)
        encoded = model.predict(scaled)
        label = label_encoder.inverse_transform(encoded)[0]
        confidence = round(max(model.predict_proba(scaled)[0]) * 100, 2)

        vitals_entry = {
            "recorded_at": datetime.utcnow(),
            "Age": data.Age,
            "SystolicBP": data.SystolicBP,
            "DiastolicBP": data.DiastolicBP,
            "BS": data.BS,
            "BodyTemp": data.BodyTemp,
            "HeartRate": data.HeartRate,
            "source": "antenatal"
        }

        prediction_entry = {
            "predicted_at": datetime.utcnow(),
            "risk": label,
            "confidence": confidence,
            "input": vitals_entry
        }

        await patients_collection.update_one(
            {"national_id": data.national_id},
            {
                "$push": {
                    "vitals_history": vitals_entry,
                    "prediction_history": prediction_entry
                },
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        if "high" in label.lower():
            send_sms(
                f"[Mama Afya] Alert: High Risk Prediction for patient {data.national_id}. Confidence: {confidence}%",
                [patient.get("phone_primary")]
            )

        return {
            "message": "Antenatal visit recorded and prediction saved",
            "risk": label,
            "confidence": confidence
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

