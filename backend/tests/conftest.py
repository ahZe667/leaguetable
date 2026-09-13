import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.deps import get_store
from app.main import app
from app.models import Base
from app.store import SqlStore


@pytest.fixture
def session_factory():
    """A throwaway in-memory SQLite database, one per test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    engine.dispose()


@pytest.fixture
def client(session_factory):
    def store_for_request():
        with session_factory() as session:
            yield SqlStore(session)

    app.dependency_overrides[get_store] = store_for_request
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def season(client):
    return client.post("/api/seasons", json={"name": "2026/27"}).json()


def add_teams(client, season_id, names):
    return [
        client.post(f"/api/seasons/{season_id}/teams", json={"name": name}).json()
        for name in names
    ]
