from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.schemas import EstuarySizeResponse

router = APIRouter(
    prefix="/estuaries",
    tags=["Estuaries"]
)

@router.get("/{estuary}/size", response_model=EstuarySizeResponse)
def get_size_distribution(estuary: str, db: Session = Depends(get_db)):
    sql = text("""
        SELECT
            sp.station_code,
            sp.latitude,
            sp.longitude,
            sw.lt_1mm AS w_lt_1mm,
            sw.mm_1_to_2_5 AS w_mm_1_to_2_5,
            sw.mm_2_5_to_5 AS w_mm_2_5_to_5,
            ss.lt_1mm AS s_lt_1mm,
            ss.mm_1_to_2_5 AS s_mm_1_to_2_5,
            ss.mm_2_5_to_5 AS s_mm_2_5_to_5
        FROM survey.survey_points sp
        LEFT JOIN survey.plastic_size_water sw
            ON sp.station_code = sw.station_code
        LEFT JOIN survey.plastic_size_sediment ss
            ON sp.station_code = ss.station_code
        WHERE sp.estuary_name = :estuary
        ORDER BY sp.station_code;
    """)

    rows = db.execute(sql, {"estuary": estuary}).mappings().all()

    # ✅ Proper 404 if estuary not found
    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"Estuary '{estuary}' not found"
        )

    points = []
    water_sum = {"lt_1mm": 0, "mm_1_to_2_5": 0, "mm_2_5_to_5": 0}
    sediment_sum = {"lt_1mm": 0, "mm_1_to_2_5": 0, "mm_2_5_to_5": 0}

    for r in rows:
        water = {
            "lt_1mm": r["w_lt_1mm"] or 0,
            "mm_1_to_2_5": r["w_mm_1_to_2_5"] or 0,
            "mm_2_5_to_5": r["w_mm_2_5_to_5"] or 0,
        }
        sediment = {
            "lt_1mm": r["s_lt_1mm"] or 0,
            "mm_1_to_2_5": r["s_mm_1_to_2_5"] or 0,
            "mm_2_5_to_5": r["s_mm_2_5_to_5"] or 0,
        }

        points.append({
            "station_code": r["station_code"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "water": water,
            "sediment": sediment,
        })

        for k in water_sum:
            water_sum[k] += water[k]
            sediment_sum[k] += sediment[k]

    n = len(rows)

    average = {
        "water": {k: round(water_sum[k] / n, 2) for k in water_sum},
        "sediment": {k: round(sediment_sum[k] / n, 2) for k in sediment_sum},
    }

    return {
        "estuary": estuary,
        "points": points,
        "average": average,
    }
