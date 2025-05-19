# app/main.py
from fastapi import Request
from fastapi import FastAPI
from app.routers import admin_router, clinician_router, chv_router,patient_router, prediction_router, antenatal_router, alert_router, sms_router,auth_router, dashboard_router
from fastapi.middleware.cors import CORSMiddleware
from app.routers.ussd_router import ussd_router
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:8000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include patient routes
app.include_router(patient_router.router)
app.include_router(prediction_router.router)
app.include_router(antenatal_router.router)
app.include_router(alert_router.router)
app.include_router(sms_router.router)
app.include_router(ussd_router)
app.include_router(admin_router.router)
app.include_router(clinician_router.router)
app.include_router(chv_router.router)
app.include_router(auth_router.router, prefix="/auth")
app.include_router(dashboard_router.router)

from app.routers.patient_router import patient_dashboard

@app.get("/dashboard", response_class=HTMLResponse)
async def alias_dashboard(request: Request):
    return await patient_dashboard(request)


