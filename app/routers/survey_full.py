from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/survey/full", tags=["Full Survey"])


@router.post("/")
def create_full_survey(
    data: schemas.FullSurveyCreate,
    db: Session = Depends(get_db)
):
    try:
        # Check duplicate station
        existing = db.query(models.SurveyPoints).filter(
            models.SurveyPoints.station_code == data.survey.station_code
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Station already exists")

        # 1️⃣ Insert survey point
        survey = models.SurveyPoints(
            estuary_id=data.survey.estuary_id,
            station_code=data.survey.station_code,
            location=data.survey.location,
            latitude=data.survey.latitude,
            longitude=data.survey.longitude,
            survey_date=data.survey.survey_date
        )
        db.add(survey)

        # 2️⃣ Insert abundance
        abundance = models.PlasticAbundance(
            station_code=data.abundance.station_code,
            water_abundance=data.abundance.water_abundance,
            sediment_abundance=data.abundance.sediment_abundance,
            sample_date=data.abundance.sample_date
        )
        db.add(abundance)

        # 3️⃣ Insert shape
        db.add(models.PlasticShapeWater(
            station_code=data.shape.station_code,
            fiber=data.shape.water.fiber,
            fragment=data.shape.water.fragment,
            film=data.shape.water.film,
            foam=data.shape.water.foam,
            pellet=data.shape.water.pellet
        ))

        db.add(models.PlasticShapeSediment(
            station_code=data.shape.station_code,
            fiber=data.shape.sediment.fiber,
            fragment=data.shape.sediment.fragment,
            film=data.shape.sediment.film,
            foam=data.shape.sediment.foam,
            pellet=data.shape.sediment.pellet
        ))

        # 4️⃣ Insert color
        db.add(models.PlasticColorWater(
            station_code=data.color.station_code,
            black=data.color.water.black,
            red=data.color.water.red,
            blue=data.color.water.blue,
            yellow=data.color.water.yellow,
            grey=data.color.water.grey,
            white=data.color.water.white,
            green=data.color.water.green,
            orange=data.color.water.orange,
            brown=data.color.water.brown,
            transparent=data.color.water.transparent
        ))

        db.add(models.PlasticColorSediment(
            station_code=data.color.station_code,
            black=data.color.sediment.black,
            red=data.color.sediment.red,
            blue=data.color.sediment.blue,
            yellow=data.color.sediment.yellow,
            grey=data.color.sediment.grey,
            white=data.color.sediment.white,
            green=data.color.sediment.green,
            orange=data.color.sediment.orange,
            brown=data.color.sediment.brown,
            transparent=data.color.sediment.transparent
        ))

        # 5️⃣ Insert size
        db.add(models.PlasticSizeWater(
            station_code=data.size.station_code,
            lt_1mm=data.size.water.lt_1mm,
            mm_1_to_2_5=data.size.water.mm_1_to_2_5,
            mm_2_5_to_5=data.size.water.mm_2_5_to_5
        ))

        db.add(models.PlasticSizeSediment(
            station_code=data.size.station_code,
            lt_1mm=data.size.sediment.lt_1mm,
            mm_1_to_2_5=data.size.sediment.mm_1_to_2_5,
            mm_2_5_to_5=data.size.sediment.mm_2_5_to_5
        ))

        db.commit()

        return {"message": "Full survey inserted successfully"}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


@router.delete("/{station_code}")
def delete_full_survey(
    station_code: str,
    db: Session = Depends(get_db)
):
    try:
        survey = db.query(models.SurveyPoints).filter(
            models.SurveyPoints.station_code == station_code
        ).first()

        water_abundance = db.query(models.PlasticAbundance).filter(
            models.PlasticAbundance.station_code == station_code
        ).first()

        shape_water = db.query(models.PlasticShapeWater).filter(
            models.PlasticShapeWater.station_code == station_code
        ).first()

        shape_sediment = db.query(models.PlasticShapeSediment).filter(
            models.PlasticShapeSediment.station_code == station_code
        ).first()

        color_water = db.query(models.PlasticColorWater).filter(
            models.PlasticColorWater.station_code == station_code
        ).first()

        color_sediment = db.query(models.PlasticColorSediment).filter(
            models.PlasticColorSediment.station_code == station_code
        ).first()

        size_water = db.query(models.PlasticSizeWater).filter(
            models.PlasticSizeWater.station_code == station_code
        ).first()

        size_sediment = db.query(models.PlasticSizeSediment).filter(
            models.PlasticSizeSediment.station_code == station_code
        ).first()

        if not any([survey, water_abundance, shape_water, shape_sediment,
                    color_water, color_sediment, size_water, size_sediment]):
            raise HTTPException(status_code=404, detail="No data found for this station")

        for entry in [size_sediment, size_water, color_sediment, color_water,
                      shape_sediment, shape_water, water_abundance, survey]:
            if entry:
                db.delete(entry)

        db.commit()

        return {"message": f"All survey data for station '{station_code}' deleted successfully"}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")