from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.schemas import EstuaryShapeResponse

router = APIRouter(
    prefix="/estuaries",
    tags=["Estuaries"]
)

@router.get("/{estuary}/shape", response_model=EstuaryShapeResponse)
def get_shape_distribution(estuary: str, db: Session = Depends(get_db)):
    sql = text("""
        SELECT
            sp.station_code,
            sp.latitude,
            sp.longitude,

            sw.fiber    AS w_fiber,
            sw.fragment AS w_fragment,
            sw.film     AS w_film,
            sw.foam     AS w_foam,
            sw.pellet   AS w_pellet,

            ss.fiber    AS s_fiber,
            ss.fragment AS s_fragment,
            ss.film     AS s_film,
            ss.foam     AS s_foam,
            ss.pellet   AS s_pellet

        FROM survey.survey_points sp
        LEFT JOIN survey.plastic_shape_water sw
            ON sp.station_code = sw.station_code
        LEFT JOIN survey.plastic_shape_sediment ss
            ON sp.station_code = ss.station_code
        WHERE sp.estuary_name = :estuary
        ORDER BY sp.station_code;
    """)

    rows = db.execute(sql, {"estuary": estuary}).mappings().all()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"Estuary '{estuary}' not found"
        )

    categories = ["fiber", "fragment", "film", "foam", "pellet"]

    points = []
    water_sum = {c: 0 for c in categories}
    sediment_sum = {c: 0 for c in categories}

    for r in rows:
        water = {c: r[f"w_{c}"] or 0 for c in categories}
        sediment = {c: r[f"s_{c}"] or 0 for c in categories}

        points.append({
            "station_code": r["station_code"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "water": water,
            "sediment": sediment,
        })

        for c in categories:
            water_sum[c] += water[c]
            sediment_sum[c] += sediment[c]

    n = len(rows)

    average = {
        "water": {c: round(water_sum[c] / n, 2) for c in categories},
        "sediment": {c: round(sediment_sum[c] / n, 2) for c in categories},
    }

    return {
        "estuary": estuary,
        "points": points,
        "average": average,
    }
