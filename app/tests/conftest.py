import pytest
from database.database import get_db, Base
from auth.authenticate import authenticate
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from api import app
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
TEST_DB_NAME = os.getenv('TEST_DB_NAME')


@pytest.fixture(name='session')
def session_fixture():
    engine = create_engine(
        f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}',
        echo=True
    )

    Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name='client')
def client_fixture(session: Session):
    def override_get_db():
        return session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[authenticate] = 'test_user@example.com'
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
