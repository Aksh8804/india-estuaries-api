from fastapi import APIRouter, Depends
from app.security import require_roles
from app import models

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/test")
def admin_test(current_user: models.User = Depends(require_roles(["admin"]))):
    return {
        "message": "Admin access granted",
        "user": current_user.username,
        "role": current_user.role
    }
