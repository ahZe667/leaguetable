def test_create_and_list_seasons(client):
    created = client.post("/api/seasons", json={"name": "2026/27"})
    assert created.status_code == 201
    assert created.json()["name"] == "2026/27"

    listed = client.get("/api/seasons")
    assert listed.status_code == 200
    assert [item["name"] for item in listed.json()] == ["2026/27"]


def test_season_names_are_unique(client):
    client.post("/api/seasons", json={"name": "2026/27"})
    clash = client.post("/api/seasons", json={"name": "2026/27"})
    assert clash.status_code == 409


def test_blank_season_name_rejected(client):
    assert client.post("/api/seasons", json={"name": "   "}).status_code == 422


def test_season_name_is_trimmed(client):
    created = client.post("/api/seasons", json={"name": "  2027/28  "})
    assert created.json()["name"] == "2027/28"
