from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
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

# ==============================================
# CONFIG
# ==============================================

BASE_URL = os.getenv(
    "BASE_URL",
    "https://india-estuaries-api.onrender.com"  # fallback
)

# ==============================================
# SCHEMAS
# ==============================================

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


# ==============================================
# REGISTER
# ==============================================

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

    # Delete old verification tokens (important fix)
    db.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == new_user.id
    ).delete()
    db.commit()

    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)

    verification_token = EmailVerificationToken(
        user_id=new_user.id,
        token=token,
        expires_at=expires_at
    )

    db.add(verification_token)
    db.commit()

    verification_link = f"{BASE_URL}/verify-email?token={token}"

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

    return {"message": "User registered successfully. Please verify your email."}


# ==============================================
# VERIFY EMAIL
# ==============================================

@router.get("/verify-email")
def verify_email(token: str = Query(...), db: Session = Depends(get_db)):
    token_entry = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == token
    ).first()

    if not token_entry:
        raise HTTPException(status_code=400, detail="Invalid token")

    if token_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expired")

    user = db.query(User).filter(
        User.id == token_entry.user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True

    db.delete(token_entry)
    db.commit()

    return RedirectResponse(
        url=f"{BASE_URL}/static/verified.html",
        status_code=302
    )


# ==============================================
# RESEND VERIFICATION
# ==============================================

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

    # Delete old tokens (important fix)
    db.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == user.id
    ).delete()
    db.commit()

    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)

    verification_token = EmailVerificationToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )

    db.add(verification_token)
    db.commit()

    verification_link = f"{BASE_URL}/verify-email?token={token}"

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


# ==============================================
# LOGIN
# ==============================================

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


# ==============================================
# LOGOUT
# ==============================================

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
        raise HTTPException(status_code=401, detail="Invalid token"}