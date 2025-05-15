from fastapi import APIRouter, Request, HTTPException
from app.routers.prediction_router import model, scaler, label_encoder
from app.db.database import predictions_collection
from datetime import datetime
import numpy as np

router = APIRouter(prefix="/sms", tags=["SMS"])

@router.post("/")
async def handle_sms(request: Request):
    try:
        form = await request.form()
        message = form.get("text") or form.get("Body")  # Support Africa's Talking & Twilio
        sender = form.get("from") or form.get("From")

        if not message:
            raise HTTPException(status_code=400, detail="No message content found")

        # Expected format: RISK <id> <sbp> <dbp> <bs> <temp> <hr>
        parts = message.strip().split()

        if parts[0].lower() != "risk" or len(parts) != 7:
            raise HTTPException(status_code=400, detail="Invalid message format")

        national_id = parts[1]
        features = list(map(float, parts[2:]))

        scaled = scaler.transform([features])
        prediction_encoded = model.predict(scaled)
        prediction_label = label_encoder.inverse_transform(prediction_encoded)[0]
        confidence = round(max(model.predict_proba(scaled)[0]) * 100, 2)

        # Save prediction
        await predictions_collection.insert_one({
            "input": {
                "national_id": national_id,
                "SystolicBP": features[0],
                "DiastolicBP": features[1],
                "BS": features[2],
                "BodyTemp": features[3],
                "HeartRate": features[4],
            },
            "predicted_risk": prediction_label,
            "confidence": confidence,
            "model_used": "xgboost",
            "predicted_at": datetime.utcnow(),
            "source": "sms",
            "sender": sender
        })

        return {
            "message": f"Prediction: {prediction_label} Risk ({confidence}%)",
            "from": sender,
            "id": national_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

