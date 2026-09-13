from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator


class Season(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class Team(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    season_id: int
    name: str


class Match(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    season_id: int
    round: int = Field(ge=1)
    home_team_id: int
    away_team_id: int
    home_score: int | None = Field(default=None, ge=0)
    away_score: int | None = Field(default=None, ge=0)

    @property
    def played(self) -> bool:
        return self.home_score is not None and self.away_score is not None


class StandingsRow(BaseModel):
    team_id: int
    team_name: str
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0
    points: int = 0

    @computed_field
    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against


class NameInput(BaseModel):
    name: str = Field(min_length=1, max_length=60)

    @model_validator(mode="after")
    def _strip(self):
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("name must not be blank")
        return self


class ResultInput(BaseModel):
    home_score: int | None = Field(default=None, ge=0)
    away_score: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _both_or_neither(self):
        if (self.home_score is None) != (self.away_score is None):
            raise ValueError("set both scores or neither")
        return self
