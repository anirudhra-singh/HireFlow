# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from app.main import app
from app.core.database import Base, get_db

# fixture starting postgresql docker container one time for the entir test session
@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16") as postgres:
        yield postgres


#fixture creates a sqlalchemy engine connected to the test container
@pytest.fixture(scope="session")
def engine(postgres_container):
    url = postgres_container.get_connection_url()
    return create_engine(url)

#fixture for creating new tables for each table and drop after test
@pytest.fixture(scope="function")
def db_session(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(engine, db_session):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()