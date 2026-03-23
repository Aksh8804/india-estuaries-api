from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/size", tags=["Size"])


@router.post("/")
def create_size(
    data: schemas.SizeCreate,
    db: Session = Depends(get_db)
):
    # Check station exists
    station = db.query(models.SurveyPoints).filter(
        models.SurveyPoints.station_code == data.station_code
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    try:
        existing = db.query(models.PlasticSizeWater).filter(
            models.PlasticSizeWater.station_code == data.station_code
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Size data already exists")

        water_entry = models.PlasticSizeWater(
            station_code=data.station_code,
            lt_1mm=data.water.lt_1mm,
            mm_1_to_2_5=data.water.mm_1_to_2_5,
            mm_2_5_to_5=data.water.mm_2_5_to_5
        )

        sediment_entry = models.PlasticSizeSediment(
            station_code=data.station_code,
            lt_1mm=data.sediment.lt_1mm,
            mm_1_to_2_5=data.sediment.mm_1_to_2_5,
            mm_2_5_to_5=data.sediment.mm_2_5_to_5
        )

        db.add(water_entry)
        db.add(sediment_entry)
        db.commit()

        return {"message": "Size data inserted successfully"}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


@router.delete("/{station_code}")
def delete_size(
    station_code: str,
    db: Session = Depends(get_db)
):
    try:
        water_entry = db.query(models.PlasticSizeWater).filter(
            models.PlasticSizeWater.station_code == station_code
        ).first()

        sediment_entry = db.query(models.PlasticSizeSediment).filter(
            models.PlasticSizeSediment.station_code == station_code
        ).first()

        if not water_entry and not sediment_entry:
            raise HTTPException(status_code=404, detail="Size data not found")

        if water_entry:
            db.delete(water_entry)
        if sediment_entry:
            db.delete(sediment_entry)

        db.commit()

        return {"message": f"Size data for station '{station_code}' deleted successfully"}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")