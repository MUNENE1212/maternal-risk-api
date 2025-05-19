from fastapi import APIRouter, Depends
from app.middleware.rbac import require_role

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard", dependencies=[Depends(require_role(["admin"]))])
async def get_admin_dashboard():
    return {"message": "Welcome Admin!"}

