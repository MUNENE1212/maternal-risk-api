# app/main.py

from fastapi import FastAPI
from app.routers import patient_router, prediction_router, antenatal_router, alert_router, sms_router
from fastapi.middleware.cors import CORSMiddleware
from app.routers.ussd_router import ussd_router

app = FastAPI()

# Include patient routes
app.include_router(patient_router.router)
app.include_router(prediction_router.router)
app.include_router(antenatal_router.router)
app.include_router(alert_router.router)
app.include_router(sms_router.router)
app.include_router(ussd_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or replace with your frontend URL for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
