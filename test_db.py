from sqlalchemy import text
from api.database import SessionLocal

db = SessionLocal()

try:
    result = db.execute(text("SELECT * FROM survey.survey_points LIMIT 1")).fetchall()
    print(result)
finally:
    db.close()
