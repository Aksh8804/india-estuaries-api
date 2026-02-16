from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session
from sqlalchemy import text

from pathlib import Path

from .database import SessionLocal
from .models import SurveyPoints
from .schemas import SurveyPointBase


app = FastAPI(title="Microplastics API")


# =========================
# CORS (IMPORTANT: EDIT THIS)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:5500",
        "https://india-estuaries-api.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# DB Session Dependency
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# HEALTH CHECK
# =========================
@app.get("/health")
def health():
    return {"status": "ok"}


# =========================
# LIST ALL ESTUARIES
# =========================
@app.get("/estuaries")
def list_estuaries(db: Session = Depends(get_db)):
    sql = text("""
        SELECT DISTINCT estuary_name
        FROM survey.survey_points
        ORDER BY estuary_name;
    """)
    rows = db.execute(sql).fetchall()
    return [r[0] for r in rows]


# =========================
# GET ALL POINTS (JSON)
# =========================
@app.get("/survey-points", response_model=list[SurveyPointBase])
def read_points(db: Session = Depends(get_db)):
    return db.query(SurveyPoints).all()


# =========================
# GET POINTS GEOJSON
# =========================
@app.get("/survey/points/geojson")
def get_points_geojson(db: Session = Depends(get_db)):
    sql = text("""
        SELECT jsonb_build_object(
            'type', 'FeatureCollection',
            'features', jsonb_agg(
                jsonb_build_object(
                    'type', 'Feature',
                    'geometry', ST_AsGeoJSON(geom)::jsonb,
                    'properties', to_jsonb(survey_points) - 'geom'
                )
            )
        ) AS geojson
        FROM survey.survey_points;
    """)
    result = db.execute(sql).scalar()

    if not result:
        return {"type": "FeatureCollection", "features": []}

    return JSONResponse(content=result)


# =========================
# GET ESTUARY ABUNDANCE
# =========================
@app.get("/estuaries/{estuary_name}")
def get_estuary_data(estuary_name: str, db: Session = Depends(get_db)):
    sql = text("""
        SELECT
            sp.point_id,
            sp.station_code,
            sp.latitude,
            sp.longitude,
            pa.water_abundance,
            pa.sediment_abundance
        FROM survey.survey_points sp
        LEFT JOIN survey.plastic_abundance pa
            ON sp.station_code = pa.station_code
        WHERE sp.estuary_name = :estuary_name
    """)
    rows = db.execute(sql, {"estuary_name": estuary_name}).fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No points found")

    water_values = [r.water_abundance for r in rows if r.water_abundance is not None]
    sediment_values = [r.sediment_abundance for r in rows if r.sediment_abundance is not None]

    return {
        "average_water_abundance": (
            sum(water_values) / len(water_values) if water_values else None
        ),
        "average_sediment_abundance": (
            sum(sediment_values) / len(sediment_values) if sediment_values else None
        ),
        "points": [
            {
                "point_id": r.point_id,
                "station_code": r.station_code,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "water_abundance": r.water_abundance,
                "sediment_abundance": r.sediment_abundance,
            }
            for r in rows
        ],
    }


# =========================
# ESTUARY SHAPE
# =========================
@app.get("/estuaries/{estuary}/shape")
def get_estuary_shape(estuary: str, db: Session = Depends(get_db)):
    sql = text("""
        SELECT
            sp.station_code,
            sp.latitude,
            sp.longitude,
            w.fiber   AS water_fiber,
            w.fragment AS water_fragment,
            w.film    AS water_film,
            w.foam    AS water_foam,
            w.pellet  AS water_pellet,
            s.fiber   AS sediment_fiber,
            s.fragment AS sediment_fragment,
            s.film    AS sediment_film,
            s.foam    AS sediment_foam,
            s.pellet  AS sediment_pellet
        FROM survey.survey_points sp
        JOIN survey.plastic_shape_water w
            ON sp.station_code = w.station_code
        JOIN survey.plastic_shape_sediment s
            ON sp.station_code = s.station_code
        WHERE sp.estuary_name = :estuary;
    """)
    rows = db.execute(sql, {"estuary": estuary}).mappings().all()

    if not rows:
        return {"estuary": estuary, "points": [], "average": {}}

    points = []
    water_sum = dict(fiber=0, fragment=0, film=0, foam=0, pellet=0)
    sediment_sum = dict(fiber=0, fragment=0, film=0, foam=0, pellet=0)

    for r in rows:
        points.append({
            "station_code": r["station_code"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "water": {
                "fiber": r["water_fiber"] or 0,
                "fragment": r["water_fragment"] or 0,
                "film": r["water_film"] or 0,
                "foam": r["water_foam"] or 0,
                "pellet": r["water_pellet"] or 0,
            },
            "sediment": {
                "fiber": r["sediment_fiber"] or 0,
                "fragment": r["sediment_fragment"] or 0,
                "film": r["sediment_film"] or 0,
                "foam": r["sediment_foam"] or 0,
                "pellet": r["sediment_pellet"] or 0,
            },
        })

        for k in water_sum:
            water_sum[k] += r[f"water_{k}"] or 0
            sediment_sum[k] += r[f"sediment_{k}"] or 0

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


# =========================
# ESTUARY COLOR
# =========================
@app.get("/estuaries/{estuary}/color")
def get_estuary_color(estuary: str, db: Session = Depends(get_db)):
    sql = text("""
        SELECT
            sp.station_code,
            sp.latitude,
            sp.longitude,
            cw.black AS w_black,
            cw.red AS w_red,
            cw.blue AS w_blue,
            cw.yellow AS w_yellow,
            cw.grey AS w_grey,
            cw.white AS w_white,
            cw.green AS w_green,
            cw.orange AS w_orange,
            cw.brown AS w_brown,
            cw.transparent AS w_transparent,
            cs.black AS s_black,
            cs.red AS s_red,
            cs.blue AS s_blue,
            cs.yellow AS s_yellow,
            cs.grey AS s_grey,
            cs.white AS s_white,
            cs.green AS s_green,
            cs.orange AS s_orange,
            cs.brown AS s_brown,
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

    points = []
    for r in rows:
        points.append({
            "station_code": r["station_code"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "water": {
                "black": r["w_black"] or 0,
                "red": r["w_red"] or 0,
                "blue": r["w_blue"] or 0,
                "yellow": r["w_yellow"] or 0,
                "grey": r["w_grey"] or 0,
                "white": r["w_white"] or 0,
                "green": r["w_green"] or 0,
                "orange": r["w_orange"] or 0,
                "brown": r["w_brown"] or 0,
                "transparent": r["w_transparent"] or 0,
            },
            "sediment": {
                "black": r["s_black"] or 0,
                "red": r["s_red"] or 0,
                "blue": r["s_blue"] or 0,
                "yellow": r["s_yellow"] or 0,
                "grey": r["s_grey"] or 0,
                "white": r["s_white"] or 0,
                "green": r["s_green"] or 0,
                "orange": r["s_orange"] or 0,
                "brown": r["s_brown"] or 0,
                "transparent": r["s_transparent"] or 0,
            },
        })

    return {"estuary": estuary, "points": points}


# =========================
# ESTUARY SIZE
# =========================
@app.get("/estuaries/{estuary}/size")
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

    points = []
    for r in rows:
        points.append({
            "station_code": r["station_code"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "water": {
                "lt_1mm": r["w_lt_1mm"] or 0,
                "mm_1_to_2_5": r["w_mm_1_to_2_5"] or 0,
                "mm_2_5_to_5": r["w_mm_2_5_to_5"] or 0,
            },
            "sediment": {
                "lt_1mm": r["s_lt_1mm"] or 0,
                "mm_1_to_2_5": r["s_mm_1_to_2_5"] or 0,
                "mm_2_5_to_5": r["s_mm_2_5_to_5"] or 0,
            },
        })

    return {"estuary": estuary, "points": points}


# =========================
# STATIC FILES
# =========================
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="static",
)

@app.get("/")
def root():
    file_path = Path(__file__).parent / "static" / "map.html"
    return FileResponse(file_path)
