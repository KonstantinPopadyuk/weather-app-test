import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db
from models import UserRequest

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session():
    # Create in-memory database
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sample_requests(db_session):
    # Create some sample requests for testing
    requests = [
        UserRequest(
            user_id="test_user_1", latitude=55.7558, longitude=37.6173, request="Moscow"
        ),
        UserRequest(
            user_id="test_user_2", latitude=55.7558, longitude=37.6173, request="Moscow"
        ),
        UserRequest(
            user_id="test_user_1",
            latitude=59.9343,
            longitude=30.3351,
            request="Saint Petersburg",
        ),
    ]

    for request in requests:
        db_session.add(request)
    db_session.commit()

    return requests
