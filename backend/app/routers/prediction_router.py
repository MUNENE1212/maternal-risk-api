from fastapi import APIRouter, HTTPException
from pydantic import BaseModel,Field
from datetime import datetime
import joblib, numpy as np, os
from app.db.database import predictions_collection, patients_collection
from typing import List

router = APIRouter(prefix="/predict", tags=["Prediction"])

# Define model paths
MODEL_PATH = "app/model/xgb_model.pkl"
SCALER_PATH = "app/model/scaler.pkl"
ENCODER_PATH = "app/model/label_encoder.pkl"

# Check existence
if not all(map(os.path.exists, [MODEL_PATH, SCALER_PATH, ENCODER_PATH])):
    raise RuntimeError("One or more model files (.pkl) are missing!")

# Load models
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
label_encoder = joblib.load(ENCODER_PATH)

# Define input model
class PredictionInput(BaseModel):
    national_id: str = Field(..., min_length=3, example="123456789")
    Age: int = Field(..., gt=10, lt=60, example=30)
    SystolicBP: int = Field(..., ge=70, le=250, example=120)
    DiastolicBP: int = Field(..., ge=40, le=150, example=80)
    BS: float = Field(..., ge=1.0, le=30.0, example=5.6)
    BodyTemp: float = Field(..., ge=35.0, le=42.0, example=36.6)
    HeartRate: int = Field(..., ge=40, le=200, example=80)

# Define response models
class PredictionHistoryItem(BaseModel):
    prediction: str
    confidence: float
    model_used: str
    predicted_at: datetime
    input: dict

class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    probabilities: List[float]
    prediction_history: List[PredictionHistoryItem]
    
@router.post("/", response_model=PredictionResponse)
async def predict(input_data: PredictionInput):
    try:
        # Prepare features for prediction
        raw_features = np.array([[
            input_data.Age,
            input_data.SystolicBP,
            input_data.DiastolicBP,
            input_data.BS,
            input_data.BodyTemp,
            input_data.HeartRate
        ]])

        # Scale and predict
        scaled = scaler.transform(raw_features)
        encoded = model.predict(scaled)
        prediction_label = label_encoder.inverse_transform(encoded)[0]
        confidence = round(max(model.predict_proba(scaled)[0]) * 100, 2)
        probabilities = model.predict_proba(scaled)[0].tolist()
        timestamp = datetime.utcnow()

        # Build prediction record (with input vitals)
        prediction_entry = PredictionHistoryItem(
            prediction=prediction_label,
            confidence=confidence,
            model_used="xgboost",
            predicted_at=timestamp,
            input=input_data.dict()
        )

        # Save to predictions collection
        await predictions_collection.insert_one({**prediction_entry.dict(), "national_id": input_data.national_id})

        # Store in patient record
        patient = await patients_collection.find_one({"_id": input_data.national_id})
        if not patient:
            new_patient = {
                "_id": input_data.national_id,
                "national_id": input_data.national_id,
                "full_name": "Unknown",
                "phone_primary": "",
                "prediction_history": [prediction_entry.dict()],
                "created_at": timestamp,
                "updated_at": timestamp,
                "submitted_by": "auto_model",
                "submitted_at": timestamp
            }
            await patients_collection.insert_one(new_patient)
        else:
            await patients_collection.update_one(
                {"_id": input_data.national_id},
                {
                    "$push": {"prediction_history": prediction_entry.dict()},
                    "$set": {"updated_at": timestamp}
                }
            )

        return {
            "prediction": prediction_label,
            "confidence": confidence,
            "probabilities": probabilities,
            "prediction_history": [prediction_entry]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

