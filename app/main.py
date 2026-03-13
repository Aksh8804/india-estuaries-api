from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session
from sqlalchemy import text

from pathlib import Path

from app.database import get_db, engine
from app.models import SurveyPoints, Base
from app.schemas import SurveyPointBase

# =========================
# IMPORT ROUTERS (CLEAN & CORRECT)
# =========================
from app.routers.estuaries_size import router as size_router
from app.routers.estuaries_abundance import router as abundance_router
from app.routers.estuaries_color import router as color_router
from app.routers.estuaries_shape import router as shape_router
from app.routers.estuaries_summary import router as summary_router
from app.routers.auth import router as auth_router
from app.routers.admin import router as admin_router
from app.routers.survey_points import router as survey_router
from app.routers.survey_full import router as survey_full_router
from app.routers.master_admin import router as master_router
from app.routers.abundance import router as abundance
from app.routers.size import router as size
from app.routers.color import router as color
from app.routers.shape import router as shape


from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend


# =========================
# CREATE TABLES (TEMPORARY)
# =========================
Base.metadata.create_all(bind=engine)

# =========================
# CREATE APP
# =========================
app = FastAPI(title="Microplastics API")

# =========================
# CORS CONFIGURATION
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ALLOW OPTIONS (CORS PREFLIGHT)
# =========================
@app.middleware("http")
async def allow_options_requests(request, call_next):
    if request.method == "OPTIONS":
        return JSONResponse(status_code=200, content={"message": "OK"})
    response = await call_next(request)
    return response

# =========================
# INCLUDE ROUTERS
# =========================
app.include_router(size_router)
app.include_router(abundance_router)
app.include_router(color_router)
app.include_router(shape_router)
app.include_router(summary_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(survey_router)
app.include_router(survey_full_router)
app.include_router(master_router)
app.include_router(abundance)
app.include_router(size)
app.include_router(color)
app.include_router(shape)

# =========================
# STARTUP CACHE
# =========================
@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())

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
# GET ALL POINTS
# =========================
@app.get("/survey-points", response_model=list[SurveyPointBase])
def read_points(db: Session = Depends(get_db)):
    return db.query(SurveyPoints).all()

# =========================
# GEOJSON ENDPOINT
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
# STATIC FILES
# =========================
BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

# =========================
# ROOT ROUTE
# =========================
@app.get("/")
def root():
    return FileResponse(BASE_DIR / "static" / "map_modified.html")