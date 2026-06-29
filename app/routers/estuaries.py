from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.security import require_roles
from app import models

router = APIRouter(
    prefix="/estuaries",
    tags=["Estuaries"]
)

@router.get("/")
def list_estuaries(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["admin", "editor", "viewer", "master_admin"]))
):
    sql = text("""
        SELECT DISTINCT estuary_name
        FROM survey.survey_points
        ORDER BY estuary_name;
    """)

    rows = db.execute(sql).fetchall()
    return [r[0] for r in rows]
    
@router.get("/{estuary_name}")
def get_estuary_metadata(
    estuary_name: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["admin", "editor", "viewer", "master_admin"]))
):
    sql = text("""
        SELECT
            estuary_id,
            estuary_name,
            state_name
        FROM survey.estuary_lookup
        WHERE estuary_name = :estuary_name;
    """)

    row = db.execute(
        sql,
        {"estuary_name": estuary_name}
    ).fetchone()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Estuary not found"
        )

    return {
        "estuary_id": row.estuary_id,
        "estuary_name": row.estuary_name,
        "state_name": row.state_name
    }

@router.post("/")
def create_estuary(
    estuary_name: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["admin", "editor"]))
):
    db.execute(
        text("""
            INSERT INTO survey.estuaries (name)
            VALUES (:name)
        """),
        {"name": estuary_name}
    )
    db.commit()

    return {"message": "Estuary created"}

@router.delete("/{estuary_name}")
def delete_estuary(
    estuary_name: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["admin"]))
):
    db.execute(
        text("""
            DELETE FROM survey.estuaries
            WHERE name = :name
        """),
        {"name": estuary_name}
    )
    db.commit()

    return {"message": "Estuary deleted"}
