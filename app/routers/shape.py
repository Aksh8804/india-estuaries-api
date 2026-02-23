from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app import models, schemas
from app.security import require_roles

router = APIRouter(prefix="/shape", tags=["Shape"])


@router.post("/")
def create_shape(
    data: schemas.PlasticShapeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin", "master_admin"]))
):
    # Check station exists
    station = db.query(models.SurveyPoints).filter(
        models.SurveyPoints.station_code == data.station_code
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    try:
        # Prevent duplicate
        existing = db.query(models.PlasticShapeWater).filter(
            models.PlasticShapeWater.station_code == data.station_code
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Shape data already exists")

        water_entry = models.PlasticShapeWater(
            station_code=data.station_code,
            fiber=data.water.fiber,
            fragment=data.water.fragment,
            film=data.water.film,
            foam=data.water.foam,
            pellet=data.water.pellet
        )

        sediment_entry = models.PlasticShapeSediment(
            station_code=data.station_code,
            fiber=data.sediment.fiber,
            fragment=data.sediment.fragment,
            film=data.sediment.film,
            foam=data.sediment.foam,
            pellet=data.sediment.pellet
        )

        db.add(water_entry)
        db.add(sediment_entry)
        db.commit()

        return {"message": "Shape data inserted successfully"}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

@router.delete("/{station_code}")
def delete_shape(
    station_code: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["master_admin"]))  # admin-only
):
    try:
        # Find the entries
        water_entry = db.query(models.PlasticShapeWater).filter(
            models.PlasticShapeWater.station_code == station_code
        ).first()

        sediment_entry = db.query(models.PlasticShapeSediment).filter(
            models.PlasticShapeSediment.station_code == station_code
        ).first()

        if not water_entry and not sediment_entry:
            raise HTTPException(status_code=404, detail="Shape data not found")

        # Delete if exists
        if water_entry:
            db.delete(water_entry)
        if sediment_entry:
            db.delete(sediment_entry)

        db.commit()

        return {"message": f"Shape data for station '{station_code}' deleted successfully"}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
