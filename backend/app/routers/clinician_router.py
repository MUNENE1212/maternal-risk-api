from fastapi import APIRouter, Depends
from app.middleware.rbac import require_role

router = APIRouter(prefix="/clinician", tags=["Clinician"])

@router.get("/dashboard", dependencies=[Depends(require_role(["clinician"]))])
async def get_clinician_dashboard():
    return {"message": "Welcome Clinician!"}

