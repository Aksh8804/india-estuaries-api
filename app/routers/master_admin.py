from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.security import require_master_admin

router = APIRouter(prefix="/master", tags=["Master Admin"])


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_master: models.User = Depends(require_master_admin)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == models.RoleEnum.master_admin:
        raise HTTPException(status_code=400, detail="Cannot delete master admin")

    db.delete(user)
    db.commit()

    return {"message": f"User '{user.username}' deleted successfully"}
    
