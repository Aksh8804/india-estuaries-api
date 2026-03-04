from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, constr
from datetime import datetime, timedelta
from jose import jwt, JWTError
import secrets
import os

from app.database import get_db
from app.models import (
    User,
    RoleEnum,
    PasswordResetToken,
    EmailVerificationToken,
    RevokedToken
)
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_master_admin,
    oauth2_scheme,
    SECRET_KEY,
    ALGORITHM
)
from app.email_service import send_email


router = APIRouter(tags=["Auth"])


# =========================================================
# SCHEMAS
# =========================================================

class UserCreate(BaseModel):
    username: str
    password: constr(min_length=8)
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: constr(min_length=8)


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class PromoteUserRequest(BaseModel):
    user_id: int
    new_role: str


# =========================================================
# REGISTER
# =========================================================

@router.post("/register")
def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        username=user_data.username,
        password=hash_password(user_data.password),
        email=user_data.email,
        role=RoleEnum.viewer,
        is_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)

    verification_token = EmailVerificationToken(
        user_id=new_user.id,
        token=token,
        expires_at=expires_at
    )

    db.add(verification_token)
    db.commit()

    verification_link = f"http://localhost:8000/verify-email?token={token}"

    html_content = f"""
    <h2>Email Verification</h2>
    <p>Click the link below to verify your email:</p>
    <a href="{verification_link}">{verification_link}</a>
    """

    background_tasks.add_task(
        send_email,
        new_user.email,
        "Verify Your Email",
        html_content
    )

    return {
        "message": "User registered successfully. Please verify your email."
    }


# =========================================================
# VERIFY EMAIL
# =========================================================

@router.get("/verify-email")
def verify_email(token: str = Query(...), db: Session = Depends(get_db)):
    token_entry = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == token
    ).first()

    if not token_entry or token_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(
        User.id == token_entry.user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    db.delete(token_entry)
    db.commit()

    from fastapi.responses import RedirectResponse

    return RedirectResponse(
        url="http://127.0.0.1:8000/static/verified.html",
        status_code=302
)


# =========================================================
# RESEND VERIFICATION
# =========================================================

@router.post("/resend-verification-email")
def resend_verification_email(
    data: ResendVerificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)

    verification_token = EmailVerificationToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )

    db.add(verification_token)
    db.commit()

    verification_link = f"http://localhost:8000/verify-email?token={token}"

    html_content = f"""
    <h2>Email Verification</h2>
    <p>Click the link below to verify your email:</p>
    <a href="{verification_link}">{verification_link}</a>
    """

    background_tasks.add_task(
        send_email,
        user.email,
        "Verify Your Email",
        html_content
    )

    return {"message": "Verification email resent successfully."}


# =========================================================
# LOGIN
# =========================================================

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified."
        )

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value}
    )

    return {"access_token": access_token, "token_type": "bearer"}


# =========================================================
# LOGOUT
# =========================================================

@router.post("/logout")
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")

        if not jti:
            raise HTTPException(status_code=400, detail="Invalid token")

        revoked_token = RevokedToken(
            jti=jti,
            expires_at=datetime.utcfromtimestamp(exp)
        )

        db.add(revoked_token)
        db.commit()

        return {"message": "Successfully logged out"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# =========================================================
# FORGOT PASSWORD
# =========================================================

@router.post("/forgot-password")
def forgot_password(
    username: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return {"message": "If the username exists, a reset link has been sent."}

    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)

    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )

    db.add(reset_token)
    db.commit()

    reset_link = f"http://127.0.0.1:8000/static/reset-password.html?token={token}"

    html_content = f"""
    <h2>Password Reset</h2>
    <p>Click below to reset your password:</p>
    <a href="{reset_link}">{reset_link}</a>
    """

    background_tasks.add_task(
        send_email,
        user.email,
        "Reset Your Password",
        html_content
    )

    return {"message": "If the username exists, a reset link has been sent."}


# =========================================================
# RESET PASSWORD
# =========================================================

@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    token_entry = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == data.token
    ).first()

    if not token_entry or token_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == token_entry.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = hash_password(data.new_password)
    db.delete(token_entry)
    db.commit()

    return {"message": "Password reset successfully"}


# =========================================================
# PROMOTE USER (MASTER ADMIN ONLY)
# =========================================================

@router.post("/promote-user", tags=["Master Admin"])
def promote_user(
    data: PromoteUserRequest,
    db: Session = Depends(get_db),
    current_master: User = Depends(require_master_admin)
):
    user = db.query(User).filter(User.id == data.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == RoleEnum.master_admin:
        raise HTTPException(status_code=400, detail="Cannot modify master admin")

    try:
        user.role = RoleEnum(data.new_role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")

    db.commit()

    return {"message": f"User promoted to {user.role.value}"}
    
# =========================================================
# VERIFY USER (MASTER ADMIN ONLY)
# =========================================================

@router.post("/verify-user", tags=["Master Admin"])
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

    # Optional: remove any pending email verification tokens
    db.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == user.id
    ).delete()

    db.commit()

    return {"message": f"User '{user.username}' verified successfully"}