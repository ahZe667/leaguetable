import pytest
from fastapi.testclient import TestClient

from app.deps import get_store
from app.main import app
from app.store import InMemoryStore


@pytest.fixture
def client():
    store = InMemoryStore()
    app.dependency_overrides[get_store] = lambda: store
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def season(client):
    return client.post("/api/seasons", json={"name": "2026/27"}).json()


def add_teams(client, season_id, names):
    return [
        client.post(f"/api/seasons/{season_id}/teams", json={"name": name}).json()
        for name in names
    ]
