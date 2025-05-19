from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import joblib, numpy as np, os
from app.db.database import predictions_collection, patients_collection

router = APIRouter(prefix="/predict", tags=["Prediction"])

# Define model paths
MODEL_PATH = "app/model/xgb_model.pkl"
SCALER_PATH = "app/model/scaler.pkl"
ENCODER_PATH = "app/model/label_encoder.pkl"

# Check existence
if not all(map(os.path.exists, [MODEL_PATH, SCALER_PATH, ENCODER_PATH])):
    raise RuntimeError("One or more model files (.pkl) are missing!")

# Load all required components
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
label_encoder = joblib.load(ENCODER_PATH)

class PredictionInput(BaseModel):
    national_id: str
    Age: int
    SystolicBP: int
    DiastolicBP: int
    BS: float
    BodyTemp: float
    HeartRate: int

@router.post("/")
async def predict(input_data: PredictionInput):
    try:
        raw_features = np.array([[
            input_data.Age,
            input_data.SystolicBP,
            input_data.DiastolicBP,
            input_data.BS,
            input_data.BodyTemp,
            input_data.HeartRate
        ]])

        scaled = scaler.transform(raw_features)
        encoded = model.predict(scaled)
        prediction_label = label_encoder.inverse_transform(encoded)[0]
        confidence = round(max(model.predict_proba(scaled)[0]) * 100, 2)

        # Create prediction record
        record = {
            "risk": prediction_label,
            "confidence": confidence,
            "model_used": "xgboost",
            "predicted_at": datetime.utcnow()
        }

        # Save to predictions collection
        await predictions_collection.insert_one({**record, "national_id": input_data.national_id})

        # Create vitals entry
        vitals = {
            **input_data.dict(exclude={"national_id"}),
            "recorded_at": datetime.utcnow(),
            "source": "prediction"
        }

        # Ensure patient exists (insert if not)
        patient = await patients_collection.find_one({"_id": input_data.national_id})
        if not patient:
            new_patient = {
                "_id": input_data.national_id,
                "national_id": input_data.national_id,
                "full_name": "Unknown",
                "phone_primary": "",
                "vitals_history": [vitals],
                "prediction_history": [record],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "submitted_by": "auto_model",
                "submitted_at": datetime.utcnow()
            }
            await patients_collection.insert_one(new_patient)
        else:
            await patients_collection.update_one(
                {"_id": input_data.national_id},
                {
                    "$push": {
                        "vitals_history": vitals,
                        "prediction_history": record
                    },
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )

        return {
            "prediction": prediction_label,
            "confidence": confidence,
            "probabilities": model.predict_proba(scaled)[0].tolist()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

