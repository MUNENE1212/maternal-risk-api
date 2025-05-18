from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.auth.auth_utils import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user=Depends(get_current_user)):
    role = user.get("role")

    if role == "admin":
        return templates.TemplateResponse("admin_dashboard.html", {"request": request, "user": user})
    elif role == "clinician":
        return templates.TemplateResponse("clinician_dashboard.html", {"request": request, "user": user})
    elif role == "chv":
        return templates.TemplateResponse("chv_dashboard.html", {"request": request, "user": user})
    elif role == "patient":
        return templates.TemplateResponse("patient_dashboard.html", {"request": request, "user": user})
    else:
        return RedirectResponse(url="/auth/login")

