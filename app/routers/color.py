from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/color", tags=["Color"])


@router.post("/")
def create_color(
    data: schemas.PlasticColorCreate,
    db: Session = Depends(get_db),
):
    # Check station exists
    station = db.query(models.SurveyPoints).filter(
        models.SurveyPoints.station_code == data.station_code
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    try:
        existing = db.query(models.PlasticColorWater).filter(
            models.PlasticColorWater.station_code == data.station_code
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Color data already exists")

        water_entry = models.PlasticColorWater(
            station_code=data.station_code,
            black=data.water.black,
            red=data.water.red,
            blue=data.water.blue,
            yellow=data.water.yellow,
            grey=data.water.grey,
            white=data.water.white,
            green=data.water.green,
            orange=data.water.orange,
            brown=data.water.brown,
            transparent=data.water.transparent
        )

        sediment_entry = models.PlasticColorSediment(
            station_code=data.station_code,
            black=data.sediment.black,
            red=data.sediment.red,
            blue=data.sediment.blue,
            yellow=data.sediment.yellow,
            grey=data.sediment.grey,
            white=data.sediment.white,
            green=data.sediment.green,
            orange=data.sediment.orange,
            brown=data.sediment.brown,
            transparent=data.sediment.transparent
        )

        db.add(water_entry)
        db.add(sediment_entry)
        db.commit()

        return {"message": "Color data inserted successfully"}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


@router.delete("/{station_code}")
def delete_color(
    station_code: str,
    db: Session = Depends(get_db),
):
    try:
        # Find the entries
        water_entry = db.query(models.PlasticColorWater).filter(
            models.PlasticColorWater.station_code == station_code
        ).first()

        sediment_entry = db.query(models.PlasticColorSediment).filter(
            models.PlasticColorSediment.station_code == station_code
        ).first()

        if not water_entry and not sediment_entry:
            raise HTTPException(status_code=404, detail="Color data not found")

        # Delete if exists
        if water_entry:
            db.delete(water_entry)
        if sediment_entry:
            db.delete(sediment_entry)

        db.commit()

        return {"message": f"Color data for station '{station_code}' deleted successfully"}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")