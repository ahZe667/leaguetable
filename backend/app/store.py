"""Persistence for the league, backed by SQLAlchemy.

The API layer only ever sees the pydantic schemas, so the storage engine can be
swapped by changing DATABASE_URL.
"""

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .errors import ConflictError, NotFoundError
from .models import MatchRow, SeasonRow, TeamRow
from .schemas import Match, Season, Team


class SqlStore:
    def __init__(self, session: Session) -> None:
        self.session = session

    # seasons -----------------------------------------------------------
    def list_seasons(self) -> list[Season]:
        rows = self.session.scalars(select(SeasonRow).order_by(SeasonRow.id)).all()
        return [Season.model_validate(row) for row in rows]

    def get_season(self, season_id: int) -> Season:
        row = self.session.get(SeasonRow, season_id)
        if row is None:
            raise NotFoundError(f"Season {season_id} not found")
        return Season.model_validate(row)

    def create_season(self, name: str) -> Season:
        row = SeasonRow(name=name)
        self.session.add(row)
        self._commit_unique(row, f"Season {name!r} already exists")
        return Season.model_validate(row)

    def _commit_unique(self, row: object, message: str) -> None:
        """Commit an insert whose uniqueness the database enforces.

        Checking first and inserting afterwards would let two concurrent
        requests past the check, so the constraint is the single arbiter.
        """
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError(message) from exc

    # teams -------------------------------------------------------------
    def list_teams(self, season_id: int) -> list[Team]:
        self.get_season(season_id)
        rows = self.session.scalars(
            select(TeamRow).where(TeamRow.season_id == season_id).order_by(TeamRow.name)
        ).all()
        return [Team.model_validate(row) for row in rows]

    def add_team(self, season_id: int, name: str) -> Team:
        self.get_season(season_id)
        if self._season_has_matches(season_id):
            raise ConflictError("Clear the fixtures before changing the teams")
        row = TeamRow(season_id=season_id, name=name)
        self.session.add(row)
        self._commit_unique(row, f"Team {name!r} is already in this season")
        return Team.model_validate(row)

    def delete_team(self, team_id: int) -> None:
        row = self.session.get(TeamRow, team_id)
        if row is None:
            raise NotFoundError(f"Team {team_id} not found")
        if self._season_has_matches(row.season_id):
            raise ConflictError("Clear the fixtures before changing the teams")
        self.session.delete(row)
        self.session.commit()

    def _season_has_matches(self, season_id: int) -> bool:
        found = self.session.scalar(select(MatchRow.id).where(MatchRow.season_id == season_id))
        return found is not None

    # matches -----------------------------------------------------------
    def list_matches(self, season_id: int) -> list[Match]:
        self.get_season(season_id)
        rows = self.session.scalars(
            select(MatchRow)
            .where(MatchRow.season_id == season_id)
            .order_by(MatchRow.round, MatchRow.id)
        ).all()
        return [Match.model_validate(row) for row in rows]

    def replace_fixtures(
        self, season_id: int, rounds: list[list[tuple[int, int]]]
    ) -> list[Match]:
        self.get_season(season_id)
        self.session.execute(delete(MatchRow).where(MatchRow.season_id == season_id))
        self.session.add_all(
            MatchRow(
                season_id=season_id,
                round=index,
                home_team_id=home_id,
                away_team_id=away_id,
            )
            for index, pairs in enumerate(rounds, start=1)
            for home_id, away_id in pairs
        )
        self.session.commit()
        return self.list_matches(season_id)

    def clear_fixtures(self, season_id: int) -> None:
        self.get_season(season_id)
        self.session.execute(delete(MatchRow).where(MatchRow.season_id == season_id))
        self.session.commit()

    def set_result(self, match_id: int, home_score: int | None, away_score: int | None) -> Match:
        row = self.session.get(MatchRow, match_id)
        if row is None:
            raise NotFoundError(f"Match {match_id} not found")
        row.home_score = home_score
        row.away_score = away_score
        self.session.commit()
        return Match.model_validate(row)
