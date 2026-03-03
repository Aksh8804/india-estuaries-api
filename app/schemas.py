from pydantic import BaseModel
from datetime import date

class SurveyPointBase(BaseModel):
    estuary_id: int | None = None
    station_code: str | None = None
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    survey_date: date | None = None
    state: str | None = None

class SurveyPoint(SurveyPointBase):
    point_id: int

    class Config:
        from_attributes = True
        
from typing import List, Optional
from pydantic import BaseModel


class EstuaryAbundancePoint(BaseModel):
    point_id: int
    station_code: str
    latitude: float
    longitude: float
    water_abundance: Optional[float] = None
    sediment_abundance: Optional[float] = None


class EstuaryAbundanceResponse(BaseModel):
    average_water_abundance: Optional[float] = None
    average_sediment_abundance: Optional[float] = None
    points: List[EstuaryAbundancePoint]


from pydantic import BaseModel
from typing import Dict, List


# =========================
# SHAPE SUB-MODELS
# =========================

class ShapeCategory(BaseModel):
    fiber: float
    fragment: float
    film: float
    foam: float
    pellet: float


class ShapePoint(BaseModel):
    station_code: str
    latitude: float
    longitude: float
    water: ShapeCategory
    sediment: ShapeCategory


class ShapeAverage(BaseModel):
    water: ShapeCategory
    sediment: ShapeCategory


class EstuaryShapeResponse(BaseModel):
    estuary: str
    points: List[ShapePoint]
    average: ShapeAverage

from pydantic import BaseModel
from typing import List


# =========================
# SIZE SUB-MODELS
# =========================

class SizeCategory(BaseModel):
    lt_1mm: float
    mm_1_to_2_5: float
    mm_2_5_to_5: float


class SizePoint(BaseModel):
    station_code: str
    latitude: float
    longitude: float
    water: SizeCategory
    sediment: SizeCategory


class EstuarySizeResponse(BaseModel):
    estuary: str
    points: List[SizePoint]
    average: dict
    
class ColorCategory(BaseModel):
    black: float
    red: float
    blue: float
    yellow: float
    grey: float
    white: float
    green: float
    orange: float
    brown: float
    transparent: float


class ColorPoint(BaseModel):
    station_code: str
    latitude: float
    longitude: float
    water: ColorCategory
    sediment: ColorCategory


class ColorAverage(BaseModel):
    water: ColorCategory
    sediment: ColorCategory


class EstuaryColorResponse(BaseModel):
    estuary: str
    points: List[ColorPoint]
    average: ColorAverage

# =========================
# USER SCHEMAS
# =========================

from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: str = Field(min_length=8, max_length=72)


class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True
        
class PlasticAbundanceCreate(BaseModel):
    station_code: str
    water_abundance: float | None = None
    sediment_abundance: float | None = None
    sample_date: date | None = None
class PlasticShapeCreate(BaseModel):
    station_code: str
    water: ShapeCategory
    sediment: ShapeCategory
class PlasticColorCreate(BaseModel):
    station_code: str
    water: ColorCategory
    sediment: ColorCategory
    
# =========================
# SURVEY CREATE SCHEMA
# =========================

class SurveyPointCreate(BaseModel):
    estuary_id: int
    station_code: str
    location: str
    latitude: float
    longitude: float
    survey_date: date
    
# =========================
# SIZE CREATE SCHEMAS
# =========================

class SizeCategoryCreate(BaseModel):
    lt_1mm: float
    mm_1_to_2_5: float
    mm_2_5_to_5: float


class SizeCreate(BaseModel):
    station_code: str
    water: SizeCategoryCreate
    sediment: SizeCategoryCreate

# =========================
# FULL SURVEY CREATE
# =========================

class FullSurveyCreate(BaseModel):
    survey: SurveyPointCreate
    abundance: PlasticAbundanceCreate
    shape: PlasticShapeCreate
    color: PlasticColorCreate
    size: SizeCreate


