from pydantic import BaseModel
from datetime import date

class SurveyPointBase(BaseModel):
    estuary_id: int | None = None
    station_code: str | None = None
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    survey_date: date | None = None

class SurveyPoint(SurveyPointBase):
    point_id: int

    class Config:
        orm_mode = True
