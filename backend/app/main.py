from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .db import init_db
from .deps import get_store
from .errors import ConflictError, NotFoundError
from .league import compute_standings, round_robin
from .schemas import Match, NameInput, ResultInput, Season, StandingsRow, Team

MIN_TEAMS = 2


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="LeagueTable API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(NotFoundError)
def _not_found(_: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
def _conflict(_: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})


@app.get("/api/seasons", response_model=list[Season])
def list_seasons(store=Depends(get_store)):
    return store.list_seasons()


@app.post("/api/seasons", response_model=Season, status_code=status.HTTP_201_CREATED)
def create_season(payload: NameInput, store=Depends(get_store)):
    return store.create_season(payload.name)


@app.get("/api/seasons/{season_id}/teams", response_model=list[Team])
def list_teams(season_id: int, store=Depends(get_store)):
    return store.list_teams(season_id)


@app.post(
    "/api/seasons/{season_id}/teams", response_model=Team, status_code=status.HTTP_201_CREATED
)
def add_team(season_id: int, payload: NameInput, store=Depends(get_store)):
    return store.add_team(season_id, payload.name)


@app.delete("/api/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: int, store=Depends(get_store)) -> Response:
    store.delete_team(team_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post(
    "/api/seasons/{season_id}/fixtures",
    response_model=list[Match],
    status_code=status.HTTP_201_CREATED,
)
def generate_fixtures(season_id: int, store=Depends(get_store)):
    teams = store.list_teams(season_id)
    if len(teams) < MIN_TEAMS:
        raise ConflictError(f"A season needs at least {MIN_TEAMS} teams")
    return store.replace_fixtures(season_id, round_robin([team.id for team in teams]))


@app.delete("/api/seasons/{season_id}/fixtures", status_code=status.HTTP_204_NO_CONTENT)
def clear_fixtures(season_id: int, store=Depends(get_store)) -> Response:
    store.clear_fixtures(season_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/seasons/{season_id}/matches", response_model=list[Match])
def list_matches(season_id: int, store=Depends(get_store)):
    return store.list_matches(season_id)


@app.put("/api/matches/{match_id}/result", response_model=Match)
def set_result(match_id: int, payload: ResultInput, store=Depends(get_store)):
    return store.set_result(match_id, payload.home_score, payload.away_score)


@app.get("/api/seasons/{season_id}/standings", response_model=list[StandingsRow])
def get_standings(season_id: int, store=Depends(get_store)):
    return compute_standings(store.list_teams(season_id), store.list_matches(season_id))
