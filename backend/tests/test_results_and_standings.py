from .conftest import add_teams

FOUR_TEAMS = ["Arrows FC", "Beacon United", "Cobblers", "Dockside Rovers"]


def prepared(client, season):
    add_teams(client, season["id"], FOUR_TEAMS)
    return client.post(f"/api/seasons/{season['id']}/fixtures").json()


def test_set_and_clear_a_result(client, season):
    match = prepared(client, season)[0]

    saved = client.put(f"/api/matches/{match['id']}/result", json={"home_score": 3, "away_score": 1})
    assert saved.status_code == 200
    assert (saved.json()["home_score"], saved.json()["away_score"]) == (3, 1)

    cleared = client.put(
        f"/api/matches/{match['id']}/result", json={"home_score": None, "away_score": None}
    )
    assert cleared.json()["home_score"] is None


def test_half_filled_and_negative_results_are_rejected(client, season):
    match = prepared(client, season)[0]
    half = client.put(f"/api/matches/{match['id']}/result", json={"home_score": 2, "away_score": None})
    negative = client.put(
        f"/api/matches/{match['id']}/result", json={"home_score": -1, "away_score": 0}
    )
    assert half.status_code == 422
    assert negative.status_code == 422


def test_result_for_unknown_match_is_not_found(client):
    assert (
        client.put("/api/matches/999/result", json={"home_score": 1, "away_score": 0}).status_code
        == 404
    )


def test_standings_start_empty_but_list_every_team(client, season):
    prepared(client, season)
    rows = client.get(f"/api/seasons/{season['id']}/standings").json()
    assert len(rows) == 4
    assert all(row["played"] == 0 and row["points"] == 0 for row in rows)


def test_standings_award_three_for_a_win_and_one_for_a_draw(client, season):
    matches = prepared(client, season)
    by_id = {match["id"]: match for match in matches}
    first, second = matches[0], matches[1]

    client.put(f"/api/matches/{first['id']}/result", json={"home_score": 3, "away_score": 1})
    client.put(f"/api/matches/{second['id']}/result", json={"home_score": 2, "away_score": 2})

    rows = {row["team_id"]: row for row in client.get(f"/api/seasons/{season['id']}/standings").json()}
    winner = rows[by_id[first["id"]]["home_team_id"]]
    loser = rows[by_id[first["id"]]["away_team_id"]]
    drawer = rows[by_id[second["id"]]["home_team_id"]]

    assert (winner["points"], winner["won"], winner["goal_difference"]) == (3, 1, 2)
    assert (loser["points"], loser["lost"], loser["goal_difference"]) == (0, 1, -2)
    assert (drawer["points"], drawer["drawn"], drawer["goal_difference"]) == (1, 1, 0)


def test_standings_order_by_points_then_goal_difference(client, season):
    matches = prepared(client, season)
    for match in matches:
        client.put(f"/api/matches/{match['id']}/result", json={"home_score": 1, "away_score": 0})

    rows = client.get(f"/api/seasons/{season['id']}/standings").json()
    points = [row["points"] for row in rows]
    differences = [row["goal_difference"] for row in rows]
    assert points == sorted(points, reverse=True)
    assert differences == sorted(differences, reverse=True)


def test_standings_ignore_matches_without_a_result(client, season):
    matches = prepared(client, season)
    client.put(f"/api/matches/{matches[0]['id']}/result", json={"home_score": 1, "away_score": 0})
    rows = client.get(f"/api/seasons/{season['id']}/standings").json()
    assert sum(row["played"] for row in rows) == 2
