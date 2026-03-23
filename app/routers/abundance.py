from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/abundance", tags=["Abundance"])


@router.post("/")
def create_abundance(
    data: schemas.PlasticAbundanceCreate,
    db: Session = Depends(get_db),
):
    # Check station exists
    station = db.query(models.SurveyPoints).filter(
        models.SurveyPoints.station_code == data.station_code
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    try:
        new_entry = models.PlasticAbundance(
            station_code=data.station_code,
            water_abundance=data.water_abundance,
            sediment_abundance=data.sediment_abundance,
            sample_date=data.sample_date
        )

        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)

        return {"message": "Abundance data inserted successfully"}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


@router.delete("/{station_code}")
def delete_abundance(
    station_code: str,
    db: Session = Depends(get_db),
):
    try:
        # Find the abundance entry for the station
        entry = db.query(models.PlasticAbundance).filter(
            models.PlasticAbundance.station_code == station_code
        ).first()

        if not entry:
            raise HTTPException(status_code=404, detail="Abundance data not found")

        # Delete the entry
        db.delete(entry)
        db.commit()

        return {"message": f"Abundance data for station '{station_code}' deleted successfully"}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")