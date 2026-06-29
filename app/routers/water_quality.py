from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db

router = APIRouter(
    prefix="/estuaries",
    tags=["Water Quality"]
)


@router.get("/{estuary_name}/water-quality")
def get_estuary_water_quality(
    estuary_name: str,
    db: Session = Depends(get_db)
):
    sql = text("""
        SELECT
            sp.point_id,
            sp.station_code,
            sp.latitude,
            sp.longitude,

            wq.sample_timestamp,
            wq.temperature_c,
            wq.ph,
            wq.orp_mv,
            wq.ec_us_cm,
            wq.tds_ppt,
            wq.salinity_psu,
            wq.dissolved_oxygen_mg_l

        FROM survey.survey_points sp
	JOIN survey.estuary_lookup el
    	    ON sp.estuary_id = el.estuary_id
	LEFT JOIN survey.water_quality wq
   	    ON sp.station_code = wq.station_code

	WHERE el.estuary_name = :estuary_name
    """)

    rows = db.execute(
        sql,
        {"estuary_name": estuary_name}
    ).fetchall()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"Estuary '{estuary_name}' not found"
        )

    def safe(val, digits=2):
        if val is None:
            return "Not available"
        if isinstance(val, float):
            return round(val, digits)
        return val

    ph_values = [
        r.ph for r in rows
        if r.ph is not None
    ]

    salinity_values = [
        r.salinity_psu for r in rows
        if r.salinity_psu is not None
    ]

    temp_values = [
        r.temperature_c for r in rows
        if r.temperature_c is not None
    ]

    do_values = [
        r.dissolved_oxygen_mg_l for r in rows
        if r.dissolved_oxygen_mg_l is not None
    ]

    return {
        "average_ph": (
            round(sum(ph_values) / len(ph_values), 2)
            if ph_values else "Not available"
        ),
        "average_salinity": (
            round(sum(salinity_values) / len(salinity_values), 2)
            if salinity_values else "Not available"
        ),
        "average_temperature": (
            round(sum(temp_values) / len(temp_values), 2)
            if temp_values else "Not available"
        ),
        "average_dissolved_oxygen": (
            round(sum(do_values) / len(do_values), 2)
            if do_values else "Not available"
        ),

        "points": [
            {
                "point_id": r.point_id,
                "station_code": r.station_code,
                "latitude": round(float(r.latitude), 6)
                if r.latitude is not None else "Not available",
                "longitude": round(float(r.longitude), 6)
                if r.longitude is not None else "Not available",

                "timestamp": r.sample_timestamp
                if r.sample_timestamp is not None else "Not available",

                
                "temperature_c": safe(r.temperature_c),
                "ph": safe(r.ph),
                "orp_mv": safe(r.orp_mv),
                "ec_us_cm": safe(r.ec_us_cm),
                "tds_ppt": safe(r.tds_ppt),
                "salinity_psu": safe(r.salinity_psu),
                "dissolved_oxygen_mg_l": safe(r.dissolved_oxygen_mg_l),
            }
            for r in rows
        ]
    }