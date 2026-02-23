from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app import models, schemas
from app.security import require_roles

router = APIRouter(prefix="/survey_points", tags=["Survey Points"])


@router.post("/")
def create_survey_point(
    data: schemas.SurveyPointCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["admin", "editor"]))
):
    # Prevent duplicate station
    existing = db.query(models.SurveyPoints).filter(
        models.SurveyPoints.station_code == data.station_code
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Station already exists")

    try:
        new_station = models.SurveyPoints(
            estuary_id=data.estuary_id,
            station_code=data.station_code,
            location=data.location,
            latitude=data.latitude,
            longitude=data.longitude,
            survey_date=data.survey_date
        )

        db.add(new_station)
        db.commit()
        db.refresh(new_station)

        return {
            "message": "Survey point created successfully",
            "station_code": data.station_code
        }

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

@router.delete("/{station_code}")
def delete_survey_point(
    station_code: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"]))  # Admin-only
):
    try:
        # Find the survey point
        survey_point = db.query(models.SurveyPoints).filter(
            models.SurveyPoints.station_code == station_code
        ).first()

        if not survey_point:
            raise HTTPException(status_code=404, detail="Survey point not found")

        db.delete(survey_point)
        db.commit()

        return {"message": f"Survey point '{station_code}' deleted successfully"}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
