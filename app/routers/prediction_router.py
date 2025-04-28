# app/routers/predict_router.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import os

router = APIRouter(prefix="/predict", tags=["Prediction"])

# Load the model
model_path = "app/model/maternal_health_risk_model.pkl"  # change if your pat
if not os.path.exists(model_path):
    raise RuntimeError("Model file not found!")

model = joblib.load(model_path)

# Define expected input fields
class PredictionInput(BaseModel):
    age: int
    pregnancies: int
    systolic_bp: float
    diastolic_bp: float
    bmi: float
    glucose: float

@router.post("/")
def predict(input_data: PredictionInput):
    try:
        features = np.array([[  # Order should match training
            input_data.age,
            input_data.pregnancies,
            input_data.systolic_bp,
            input_data.diastolic_bp,
            input_data.bmi,
            input_data.glucose
        ]])
        prediction = model.predict(features)
        probability = model.predict_proba(features)[0].tolist()

        return {
            "prediction": int(prediction[0]),
            "probabilities": probability
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

