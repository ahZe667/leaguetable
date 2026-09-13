from .conftest import add_teams


def test_add_and_list_teams_sorted_by_name(client, season):
    add_teams(client, season["id"], ["Cobblers", "Arrows FC"])
    response = client.get(f"/api/seasons/{season['id']}/teams")
    assert [team["name"] for team in response.json()] == ["Arrows FC", "Cobblers"]


def test_team_names_are_unique_within_a_season(client, season):
    client.post(f"/api/seasons/{season['id']}/teams", json={"name": "Arrows FC"})
    clash = client.post(f"/api/seasons/{season['id']}/teams", json={"name": "Arrows FC"})
    assert clash.status_code == 409


def test_same_team_name_allowed_in_another_season(client, season):
    other = client.post("/api/seasons", json={"name": "2027/28"}).json()
    client.post(f"/api/seasons/{season['id']}/teams", json={"name": "Arrows FC"})
    accepted = client.post(f"/api/seasons/{other['id']}/teams", json={"name": "Arrows FC"})
    assert accepted.status_code == 201


def test_unknown_season_is_not_found(client):
    assert client.get("/api/seasons/999/teams").status_code == 404
    assert client.post("/api/seasons/999/teams", json={"name": "Arrows FC"}).status_code == 404


def test_delete_team(client, season):
    team = client.post(f"/api/seasons/{season['id']}/teams", json={"name": "Arrows FC"}).json()
    assert client.delete(f"/api/teams/{team['id']}").status_code == 204
    assert client.get(f"/api/seasons/{season['id']}/teams").json() == []


def test_delete_unknown_team_is_not_found(client):
    assert client.delete("/api/teams/999").status_code == 404


def test_cannot_delete_a_team_once_fixtures_exist(client, season):
    teams = add_teams(client, season["id"], ["Arrows FC", "Beacon United"])
    client.post(f"/api/seasons/{season['id']}/fixtures")
    assert client.delete(f"/api/teams/{teams[0]['id']}").status_code == 409
