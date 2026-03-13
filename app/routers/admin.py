from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, RoleEnum
from app.security import require_master_admin


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# =========================================================
# GET ALL USERS
# =========================================================

@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    current_master: User = Depends(require_master_admin)
):
    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "is_verified": user.is_verified
        }
        for user in users
    ]


# =========================================================
# VERIFY USER
# =========================================================

@router.post("/verify-user")
def verify_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_master: User = Depends(require_master_admin)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="User already verified")

    user.is_verified = True
    db.commit()

    return {"message": f"User '{user.username}' verified successfully"}


# =========================================================
# PROMOTE USER
# =========================================================

@router.post("/promote-user")
def promote_user(
    user_id: int,
    new_role: str,
    db: Session = Depends(get_db),
    current_master: User = Depends(require_master_admin)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == RoleEnum.master_admin:
        raise HTTPException(status_code=400, detail="Cannot modify master admin")

    try:
        user.role = RoleEnum(new_role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")

    db.commit()

    return {"message": f"User promoted to {user.role.value}"}


# =========================================================
# ADMIN DASHBOARD STATS
# =========================================================

@router.get("/stats")
def admin_stats(
    db: Session = Depends(get_db),
    current_master: User = Depends(require_master_admin)
):
    total_users = db.query(User).count()

    verified_users = db.query(User).filter(
        User.is_verified == True
    ).count()

    unverified_users = db.query(User).filter(
        User.is_verified == False
    ).count()

    return {
        "total_users": total_users,
        "verified_users": verified_users,
        "unverified_users": unverified_users
    }


# =========================================================
# STATE-WISE USER COUNT
# =========================================================

@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    current_master: User = Depends(require_master_admin)
):
    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "is_verified": user.is_verified
        }
        for user in users
    ]