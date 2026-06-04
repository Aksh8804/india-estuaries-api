from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.schemas import EstuaryAbundanceResponse

router = APIRouter(
    prefix="/estuaries",
    tags=["Estuaries"]
)

@router.get("/{estuary_name}/abundance", response_model=EstuaryAbundanceResponse)
def get_estuary_abundance(estuary_name: str, db: Session = Depends(get_db)):
    sql = text("""
        SELECT
            sp.point_id,
            sp.station_code,
            sp.latitude,
            sp.longitude,
            sp.state,   -- 👈 ADD THIS
            pa.water_abundance,
            pa.sediment_abundance
        FROM survey.survey_points sp
        LEFT JOIN survey.plastic_abundance pa
            ON sp.station_code = pa.station_code
        WHERE sp.estuary_name = :estuary_name
    """)

    rows = db.execute(sql, {"estuary_name": estuary_name}).fetchall()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"Estuary '{estuary_name}' not found"
        )

    water_values = [r.water_abundance for r in rows if r.water_abundance is not None]
    sediment_values = [r.sediment_abundance for r in rows if r.sediment_abundance is not None]

    return {
        "average_water_abundance": (
            round(sum(water_values) / len(water_values), 2) if water_values else None
        ),
        "average_sediment_abundance": (
            round(sum(sediment_values) / len(sediment_values), 2) if sediment_values else None
        ),
        "points": [
            {
                "point_id": r.point_id,
                "station_code": r.station_code,
                "latitude": round(r.latitude, 6) if r.latitude else None,
                "longitude": round(r.longitude, 6) if r.longitude else None,
                "water_abundance": round(r.water_abundance, 2) if r.water_abundance else None,
                "sediment_abundance": round(r.sediment_abundance, 2) if r.sediment_abundance else None,
            }
            for r in rows
        ],
    }