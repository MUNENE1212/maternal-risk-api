from fastapi import APIRouter, Depends
from app.middleware.rbac import require_role

router = APIRouter(prefix="/chv", tags=["CHV"])

@router.get("/dashboard", dependencies=[Depends(require_role(["chv"]))])
async def chv_dashboard():
    return {"message": "CHV  Dashboard"}

