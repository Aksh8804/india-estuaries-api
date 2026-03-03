from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Numeric,
    Enum as SQLEnum,
    ForeignKey,
    Boolean
)
from sqlalchemy.orm import relationship
from .database import Base
import enum


# =========================
# Survey Models
# =========================

class SurveyPoints(Base):
    __tablename__ = "survey_points"
    __table_args__ = {"schema": "survey"}

    point_id = Column(Integer, primary_key=True, index=True)
    estuary_id = Column(Integer)
    station_code = Column(String(50))
    location = Column(String(255))
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    survey_date = Column(Date)
    state = Column(String(100), nullable=False)


class PlasticAbundance(Base):
    __tablename__ = "plastic_abundance"
    __table_args__ = {"schema": "survey"}

    abundance_id = Column(Integer, primary_key=True, index=True)
    station_code = Column(String(50), nullable=False)
    water_abundance = Column(Numeric)
    sediment_abundance = Column(Numeric)
    sample_date = Column(Date)


class PlasticShapeWater(Base):
    __tablename__ = "plastic_shape_water"
    __table_args__ = {"schema": "survey"}

    station_code = Column(String(50), primary_key=True)
    fiber = Column(Numeric)
    fragment = Column(Numeric)
    film = Column(Numeric)
    foam = Column(Numeric)
    pellet = Column(Numeric)


class PlasticShapeSediment(Base):
    __tablename__ = "plastic_shape_sediment"
    __table_args__ = {"schema": "survey"}

    station_code = Column(String(50), primary_key=True)
    fiber = Column(Numeric)
    fragment = Column(Numeric)
    film = Column(Numeric)
    foam = Column(Numeric)
    pellet = Column(Numeric)


class PlasticColorWater(Base):
    __tablename__ = "plastic_color_water"
    __table_args__ = {"schema": "survey"}

    station_code = Column(String(50), primary_key=True)
    black = Column(Numeric)
    red = Column(Numeric)
    blue = Column(Numeric)
    yellow = Column(Numeric)
    grey = Column(Numeric)
    white = Column(Numeric)
    green = Column(Numeric)
    orange = Column(Numeric)
    brown = Column(Numeric)
    transparent = Column(Numeric)


class PlasticColorSediment(Base):
    __tablename__ = "plastic_color_sediment"
    __table_args__ = {"schema": "survey"}

    station_code = Column(String(50), primary_key=True)
    black = Column(Numeric)
    red = Column(Numeric)
    blue = Column(Numeric)
    yellow = Column(Numeric)
    grey = Column(Numeric)
    white = Column(Numeric)
    green = Column(Numeric)
    orange = Column(Numeric)
    brown = Column(Numeric)
    transparent = Column(Numeric)


class PlasticSizeWater(Base):
    __tablename__ = "plastic_size_water"
    __table_args__ = {"schema": "survey"}

    station_code = Column(String, primary_key=True)
    lt_1mm = Column(Numeric)
    mm_1_to_2_5 = Column(Numeric)
    mm_2_5_to_5 = Column(Numeric)


class PlasticSizeSediment(Base):
    __tablename__ = "plastic_size_sediment"
    __table_args__ = {"schema": "survey"}

    station_code = Column(String, primary_key=True)
    lt_1mm = Column(Numeric)
    mm_1_to_2_5 = Column(Numeric)
    mm_2_5_to_5 = Column(Numeric)


# =========================
# User & Auth Models
# =========================

class RoleEnum(str, enum.Enum):
    master_admin = "master_admin"
    admin = "admin"
    editor = "editor"
    viewer = "viewer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    role = Column(SQLEnum(RoleEnum), nullable=False)
    email = Column(String, unique=True, nullable=True, index=True)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Relationships
    password_reset_tokens = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    email_verification_tokens = relationship(
        "EmailVerificationToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="password_reset_tokens")


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="email_verification_tokens")

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
