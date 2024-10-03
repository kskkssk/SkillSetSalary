import pandas as pd

from worker.celery_config import app
from app.services.crud.person_service import PersonService
from app.database.database import get_db
from app.models.user import User


@app.task
def handle_request(data: pd.DataFrame, username: str):
    db = get_db()
    session = next(db)
    try:
        user = session.query(User).filter_by(username=username).first()
        if user is None:
            raise ValueError("User not found")
        person_service = PersonService(session, user)
        result = person_service.handle_request(data)
        return result
    finally:
        db.close()