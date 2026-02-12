from sqlalchemy import Column, Integer, String, Date, Numeric
from sqlalchemy.orm import relationship
from .database import Base

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