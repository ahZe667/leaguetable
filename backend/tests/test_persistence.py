from sqlalchemy import select

from app.models import MatchRow, SeasonRow, TeamRow

from .conftest import add_teams


def test_written_data_is_visible_to_a_fresh_session(client, session_factory, season):
    add_teams(client, season["id"], ["Arrows FC", "Beacon United"])
    matches = client.post(f"/api/seasons/{season['id']}/fixtures").json()
    client.put(
        f"/api/matches/{matches[0]['id']}/result", json={"home_score": 2, "away_score": 0}
    )

    with session_factory() as session:
        assert session.scalars(select(SeasonRow.name)).all() == ["2026/27"]
        assert sorted(session.scalars(select(TeamRow.name)).all()) == [
            "Arrows FC",
            "Beacon United",
        ]
        stored = session.scalars(select(MatchRow)).all()

    assert len(stored) == 1
    assert (stored[0].home_score, stored[0].away_score) == (2, 0)


def test_regenerating_fixtures_removes_the_old_rows(client, session_factory, season):
    add_teams(client, season["id"], ["Arrows FC", "Beacon United", "Cobblers"])
    client.post(f"/api/seasons/{season['id']}/fixtures")
    client.post(f"/api/seasons/{season['id']}/fixtures")

    with session_factory() as session:
        assert len(session.scalars(select(MatchRow)).all()) == 3


def test_deleting_a_team_removes_only_that_row(client, session_factory, season):
    teams = add_teams(client, season["id"], ["Arrows FC", "Beacon United"])
    client.delete(f"/api/teams/{teams[0]['id']}")

    with session_factory() as session:
        assert session.scalars(select(TeamRow.name)).all() == ["Beacon United"]
