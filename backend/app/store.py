"""In-memory store standing in for the database.

Replaced by a SQLAlchemy-backed implementation with the same interface.
"""

from itertools import count

from .errors import ConflictError, NotFoundError
from .schemas import Match, Season, Team


class InMemoryStore:
    def __init__(self) -> None:
        self._ids = count(1)
        self._seasons: dict[int, Season] = {}
        self._teams: dict[int, Team] = {}
        self._matches: dict[int, Match] = {}

    def _next_id(self) -> int:
        return next(self._ids)

    # seasons -----------------------------------------------------------
    def list_seasons(self) -> list[Season]:
        return sorted(self._seasons.values(), key=lambda season: season.id)

    def get_season(self, season_id: int) -> Season:
        season = self._seasons.get(season_id)
        if season is None:
            raise NotFoundError(f"Season {season_id} not found")
        return season

    def create_season(self, name: str) -> Season:
        if any(season.name == name for season in self._seasons.values()):
            raise ConflictError(f"Season {name!r} already exists")
        season = Season(id=self._next_id(), name=name)
        self._seasons[season.id] = season
        return season

    # teams -------------------------------------------------------------
    def list_teams(self, season_id: int) -> list[Team]:
        self.get_season(season_id)
        teams = [team for team in self._teams.values() if team.season_id == season_id]
        return sorted(teams, key=lambda team: team.name)

    def add_team(self, season_id: int, name: str) -> Team:
        self.get_season(season_id)
        clash = any(
            team.season_id == season_id and team.name == name for team in self._teams.values()
        )
        if clash:
            raise ConflictError(f"Team {name!r} is already in this season")
        team = Team(id=self._next_id(), season_id=season_id, name=name)
        self._teams[team.id] = team
        return team

    def delete_team(self, team_id: int) -> None:
        team = self._teams.get(team_id)
        if team is None:
            raise NotFoundError(f"Team {team_id} not found")
        if self._season_has_matches(team.season_id):
            raise ConflictError("Remove the fixtures before changing the teams")
        del self._teams[team_id]

    def _season_has_matches(self, season_id: int) -> bool:
        return any(match.season_id == season_id for match in self._matches.values())

    # matches -----------------------------------------------------------
    def list_matches(self, season_id: int) -> list[Match]:
        self.get_season(season_id)
        matches = [match for match in self._matches.values() if match.season_id == season_id]
        return sorted(matches, key=lambda match: (match.round, match.id))

    def replace_fixtures(
        self, season_id: int, rounds: list[list[tuple[int, int]]]
    ) -> list[Match]:
        self.get_season(season_id)
        self._matches = {
            key: match for key, match in self._matches.items() if match.season_id != season_id
        }
        for index, pairs in enumerate(rounds, start=1):
            for home_id, away_id in pairs:
                match = Match(
                    id=self._next_id(),
                    season_id=season_id,
                    round=index,
                    home_team_id=home_id,
                    away_team_id=away_id,
                )
                self._matches[match.id] = match
        return self.list_matches(season_id)

    def set_result(self, match_id: int, home_score: int | None, away_score: int | None) -> Match:
        match = self._matches.get(match_id)
        if match is None:
            raise NotFoundError(f"Match {match_id} not found")
        match.home_score = home_score
        match.away_score = away_score
        return match
