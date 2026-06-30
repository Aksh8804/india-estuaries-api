from datetime import datetime, timedelta
from typing import Optional, List
import uuid
import os

from jose import JWTError, jwt
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database import get_db
from app import models


# =========================
# CONFIG
# =========================

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable not set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# =========================
# PASSWORD HASHING
# =========================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# =========================
# JWT TOKEN CREATION
# =========================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4())  # Unique token ID for revocation
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload

    except JWTError as e:
        print("JWT ERROR:", repr(e))
        return None


# =========================
# AUTH DEPENDENCIES
# =========================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    print("TOKEN:", token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    print("PAYLOAD:", payload)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    jti: str = payload.get("jti")

    if username is None or jti is None:
        raise credentials_exception

    # 🔒 Check if token is revoked
    revoked_token = db.query(models.RevokedToken).filter(
        models.RevokedToken.jti == jti
    ).first()

    if revoked_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )

    user = db.query(models.User).filter(
        models.User.username == username
    ).first()
    print("USER:", user)

    if user is None:
        raise credentials_exception

    return user


# =========================
# ADMIN CHECK
# =========================

def get_current_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.RoleEnum.admin:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    return current_user


# =========================
# ROLE-BASED ACCESS CONTROL
# =========================

def require_roles(allowed_roles):
    """
    Accepts:
    - Single string: "admin"
    - List of strings: ["admin", "master_admin"]
    - RoleEnum values
    """

    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    allowed_enum_roles = [
        models.RoleEnum(role) if isinstance(role, str) else role
        for role in allowed_roles
    ]

    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role not in allowed_enum_roles:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions"
            )
        return current_user

    return role_checker


# =========================
# MASTER ADMIN CHECK
# =========================

def require_master_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.RoleEnum.master_admin:
        raise HTTPException(
            status_code=403,
            detail="Only master admin can perform this action"
        )
    return current_user


# =========================
# ADMIN POST ONLY CHECK
# =========================

def require_admin_post_only(current_user: models.User = Depends(get_current_user)):
    """
    Allows:
    - admin
    - master_admin
    Prevents:
    - viewer
    """
    if current_user.role not in [
        models.RoleEnum.admin,
        models.RoleEnum.master_admin
    ]:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )
    return current_user