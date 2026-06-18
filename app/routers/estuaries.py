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
