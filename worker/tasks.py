from worker.celery_config import app
from services.crud.person_service import PersonService
from database.database import get_db
from models.user import User


@app.task
def handle_request(pdf_path: str, email: str):
    db = get_db()
    session = next(db)
    try:
        user = session.query(User).filter_by(email=email).first()
        if user is None:
            raise ValueError("User not found")
        person_service = PersonService(session, user)
        result = person_service.handle_request(pdf_path)
        return result
    finally:
        db.close()


@app.task(max_memory_per_child=100)
def handle_interpret(pdf_path: str, email: str):
    db = get_db()
    session = next(db)
    try:
        user = session.query(User).filter_by(email=email).first()
        if user is None:
            raise ValueError("User not found")
        person_service = PersonService(session, user)
        skills_improve, skills_advice = person_service.handle_interpret(pdf_path)
    finally:
        db.close()
    return skills_improve, skills_advice

