# app/main.py

from fastapi import FastAPI
from app.routers import patient_router, prediction_router


app = FastAPI()

# Include patient routes
app.include_router(patient_router.router)
app.include_router(prediction_router.router)

