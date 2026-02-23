from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.schemas import EstuaryColorResponse

router = APIRouter(
    prefix="/estuaries",
    tags=["Estuaries"]
)

@router.get("/{estuary}/color", response_model=EstuaryColorResponse)
def get_color_distribution(estuary: str, db: Session = Depends(get_db)):
    sql = text("""
        SELECT
            sp.station_code,
            sp.latitude,
            sp.longitude,

            cw.black   AS w_black,
            cw.red     AS w_red,
            cw.blue    AS w_blue,
            cw.yellow  AS w_yellow,
            cw.grey    AS w_grey,
            cw.white   AS w_white,
            cw.green   AS w_green,
            cw.orange  AS w_orange,
            cw.brown   AS w_brown,
            cw.transparent AS w_transparent,

            cs.black   AS s_black,
            cs.red     AS s_red,
            cs.blue    AS s_blue,
            cs.yellow  AS s_yellow,
            cs.grey    AS s_grey,
            cs.white   AS s_white,
            cs.green   AS s_green,
            cs.orange  AS s_orange,
            cs.brown   AS s_brown,
            cs.transparent AS s_transparent

        FROM survey.survey_points sp
        LEFT JOIN survey.plastic_color_water cw
            ON sp.station_code = cw.station_code
        LEFT JOIN survey.plastic_color_sediment cs
            ON sp.station_code = cs.station_code
        WHERE sp.estuary_name = :estuary
        ORDER BY sp.station_code;
    """)

    rows = db.execute(sql, {"estuary": estuary}).mappings().all()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"Estuary '{estuary}' not found"
        )

    categories = [
        "black", "red", "blue", "yellow", "grey",
        "white", "green", "orange", "brown", "transparent"
    ]

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
