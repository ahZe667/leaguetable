# LeagueTable – Specification

## Idea

A scoreboard for an amateur sports league: keep the teams, generate the fixture
list, enter results as they are played, and see the standings recalculated
automatically.

## Scope decisions

- One league, many seasons. A season owns its own teams, fixtures and table.
- Football scoring: 3 points for a win, 1 for a draw, 0 for a loss.
- Fixtures are generated automatically as a single round-robin once the teams
  are known. Results are filled in afterwards.
- No authentication, no user accounts. Anyone with the URL can edit.
- Frontend and backend are separate applications talking over a REST API
  described by `openapi.yaml`.

## Domain model

- **Season** – `id`, `name` (for example `2026/27`).
- **Team** – `id`, `season_id`, `name`. Unique per season.
- **Match** – `id`, `season_id`, `round`, `home_team_id`, `away_team_id`,
  `home_score`, `away_score`. Scores are null until the match is played.
- **Standings row** – computed, never stored: played, won, drawn, lost, goals
  for, goals against, goal difference, points.

## Features

1. **Seasons** – create a season, list seasons, switch the active season.
2. **Teams** – add and remove teams within the selected season. Teams can only
   be removed while no fixtures exist.
3. **Fixture generation** – generate a single round-robin schedule for the
   season's teams using the circle method. An odd number of teams gives one bye
   per round. Regenerating replaces the existing schedule and clears results.
4. **Results** – enter or correct the score of any fixture. Clearing a score
   returns the match to the not-played state.
5. **Standings** – table computed from played matches only, sorted by points,
   then goal difference, then goals scored, then team name.

## Out of scope

- Logins, roles, permissions.
- Player-level statistics, cards, substitutions.
- Double round-robin, play-offs, promotion and relegation.
- Live updates pushed to the browser. A page refresh is enough.

## Tech

- **Frontend** – React with Vite, plain JavaScript. All backend calls live in
  `frontend/src/api.js`.
- **Backend** – FastAPI, managed with `uv`. SQLAlchemy over SQLite, so the
  database can be swapped later.
- **Contract** – `openapi.yaml` at the repository root is the source of truth
  for the API.

## API surface

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/seasons` | List seasons |
| POST | `/api/seasons` | Create a season |
| GET | `/api/seasons/{id}/teams` | List teams in a season |
| POST | `/api/seasons/{id}/teams` | Add a team |
| DELETE | `/api/teams/{id}` | Remove a team |
| POST | `/api/seasons/{id}/fixtures` | Generate the round-robin schedule |
| DELETE | `/api/seasons/{id}/fixtures` | Clear the schedule |
| GET | `/api/seasons/{id}/matches` | List matches, ordered by round |
| PUT | `/api/matches/{id}/result` | Set or clear a result |
| GET | `/api/seasons/{id}/standings` | Computed table |
