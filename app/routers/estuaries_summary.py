from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from fastapi_cache.decorator import cache


# Import existing route functions
from app.routers.estuaries_size import get_size_distribution
from app.routers.estuaries_abundance import get_estuary_abundance
from app.routers.estuaries_color import get_color_distribution
from app.routers.estuaries_shape import get_shape_distribution

router = APIRouter(
    prefix="/estuaries",
    tags=["Estuaries"]
)

@router.get("/{estuary}/summary")
@cache(expire=300)  # 5 minutes cache
def get_estuary_summary(estuary: str, db: Session = Depends(get_db)):

    try:
        abundance = get_estuary_abundance(estuary, db)
        size = get_size_distribution(estuary, db)
        color = get_color_distribution(estuary, db)
        shape = get_shape_distribution(estuary, db)

    except HTTPException as e:
        raise e

    return {
        "estuary": estuary,
        "abundance": abundance,
        "size": size,
        "color": color,
        "shape": shape,
    }
