# dashboard_router.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.auth.auth_utils import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)  # Single endpoint for all roles
async def unified_dashboard(request: Request, user=Depends(get_current_user)):
    role = user.get("role", "patient").lower()
    
    template_map = {
        "admin": "admin_dashboard.html",
        "clinician": "clinician_dashboard.html",
        "chv": "chv_dashboard.html",
        "patient": "mother_dashboard.html",
        "mother": "mother_dashboard.html"  # Alias for patient
    }
    
    template = template_map.get(role, "mother_dashboard.html")
    return templates.TemplateResponse(template, {"request": request, "user": user})
