import pytest

from app.league import round_robin

from .conftest import add_teams

FOUR_TEAMS = ["Arrows FC", "Beacon United", "Cobblers", "Dockside Rovers"]


@pytest.mark.parametrize(
    ("team_count", "expected_rounds", "expected_matches"),
    [(2, 1, 1), (4, 3, 6), (5, 5, 10), (6, 5, 15)],
)
def test_round_robin_pairs_every_team_once(team_count, expected_rounds, expected_matches):
    ids = list(range(1, team_count + 1))
    rounds = round_robin(ids)

    assert len(rounds) == expected_rounds
    pairs = [pair for round_pairs in rounds for pair in round_pairs]
    assert len(pairs) == expected_matches
    assert len({frozenset(pair) for pair in pairs}) == expected_matches


def test_round_robin_never_repeats_a_team_within_a_round():
    for round_pairs in round_robin([1, 2, 3, 4, 5]):
        appearing = [team for pair in round_pairs for team in pair]
        assert len(appearing) == len(set(appearing))


def test_generate_fixtures_creates_the_full_schedule(client, season):
    add_teams(client, season["id"], FOUR_TEAMS)
    response = client.post(f"/api/seasons/{season['id']}/fixtures")

    assert response.status_code == 201
    matches = response.json()
    assert len(matches) == 6
    assert sorted({match["round"] for match in matches}) == [1, 2, 3]
    assert all(match["home_score"] is None for match in matches)


def test_generating_again_replaces_the_schedule_and_clears_results(client, season):
    add_teams(client, season["id"], FOUR_TEAMS)
    first = client.post(f"/api/seasons/{season['id']}/fixtures").json()
    client.put(
        f"/api/matches/{first[0]['id']}/result", json={"home_score": 1, "away_score": 0}
    )

    second = client.post(f"/api/seasons/{season['id']}/fixtures").json()
    assert len(second) == 6
    assert all(match["home_score"] is None for match in second)
    assert client.get(f"/api/seasons/{season['id']}/standings").json()[0]["played"] == 0


def test_clearing_fixtures_of_an_unknown_season_is_not_found(client):
    assert client.delete("/api/seasons/999/fixtures").status_code == 404


def test_fixtures_need_at_least_two_teams(client, season):
    add_teams(client, season["id"], ["Arrows FC"])
    assert client.post(f"/api/seasons/{season['id']}/fixtures").status_code == 409


def test_matches_are_listed_in_round_order(client, season):
    add_teams(client, season["id"], FOUR_TEAMS)
    client.post(f"/api/seasons/{season['id']}/fixtures")
    rounds = [match["round"] for match in client.get(f"/api/seasons/{season['id']}/matches").json()]
    assert rounds == sorted(rounds)
