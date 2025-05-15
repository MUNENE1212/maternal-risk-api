from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse
from app.db.database import patients_collection
from app.routers.prediction_router import (
    model, scaler, label_encoder, PredictionHistoryItem, PredictionInput
)
from datetime import datetime
import numpy as np

ussd_router = APIRouter(prefix="/ussd", tags=["USSD"])

@ussd_router.post("/", response_class=PlainTextResponse)
async def ussd_handler(
    sessionId: str = Form(...),
    serviceCode: str = Form(...),
    phoneNumber: str = Form(...),
    text: str = Form(...)
):
    try:
        parts = text.strip().split("*")
        if len(parts) != 7:
            return "END Invalid input format. Please enter: ID*Age*Systolic*Diastolic*BS*Temp*HR"

        national_id, age, sys_bp, dias_bp, bs, temp, hr = parts
        input_data = PredictionInput(
            national_id=national_id,
            Age=int(age),
            SystolicBP=int(sys_bp),
            DiastolicBP=int(dias_bp),
            BS=float(bs),
            BodyTemp=float(temp),
            HeartRate=int(hr)
        )

        # Make prediction
        features = np.array([[
            input_data.Age,
            input_data.SystolicBP,
            input_data.DiastolicBP,
            input_data.BS,
            input_data.BodyTemp,
            input_data.HeartRate
        ]])
        scaled = scaler.transform(features)
        encoded = model.predict(scaled)
        prediction_label = label_encoder.inverse_transform(encoded)[0]
        confidence = round(max(model.predict_proba(scaled)[0]) * 100, 2)

        # Construct prediction item
        prediction_history_item = PredictionHistoryItem(
            risk=prediction_label,
            confidence=confidence,
            model_used="xgboost",
            predicted_at=datetime.utcnow(),
            input=input_data.dict()
        )

        # Update patient record or create one
        await patients_collection.update_one(
            {"_id": national_id},
            {
                "$set": {
                    "updated_at": datetime.utcnow(),
                    "phone_primary": phoneNumber.strip().replace("+", "")
                },
                "$push": {
                    "prediction_history": prediction_history_item.dict()
                },
                "$setOnInsert": {
                    "national_id": national_id,
                    "full_name": "Unknown",
                    "created_at": datetime.utcnow(),
                    "submitted_by": "ussd",
                    "submitted_at": datetime.utcnow(),
                    "vitals_history": [],
                }
            },
            upsert=True
        )

        return f"END Risk: {prediction_label.upper()} ({confidence}%)"

    except Exception as e:
        print("Prediction error from USSD:", e)
        return "END Error occurred during prediction. Try again later."

