# LeagueTable

A scoreboard for an amateur sports league: manage seasons and teams, generate a
round-robin fixture list, enter results, and watch the standings recalculate.

Homework 2 of the [AI Dev Tools Zoomcamp 2026](https://courses.datatalks.club/ai-dev-tools-2026/)
by DataTalksClub. Built spec-first with Claude Code.

- Specification: [`_docs/specs.md`](_docs/specs.md)
- API contract: [`openapi.yaml`](openapi.yaml)
- Agent instructions: [`AGENTS.md`](AGENTS.md)

## Running

Backend, from `backend/`:

```bash
uv sync
uv run uvicorn app.main:app --reload
```

Frontend, from `frontend/`:

```bash
npm install
npm run dev
```

The frontend runs on http://localhost:5173 and talks to the backend on
http://localhost:8000.

## Configuration

Both settings have working defaults, so nothing is required for local use.

| Variable | Used by | Default |
| --- | --- | --- |
| `DATABASE_URL` | backend | `sqlite:///./leaguetable.db` |
| `VITE_API_URL` | frontend | `http://localhost:8000` |

The backend talks to the database through SQLAlchemy only, so pointing
`DATABASE_URL` at PostgreSQL needs no code change.

## Tests

```bash
cd backend && uv run pytest
```

Thirty four tests cover the endpoints, the round-robin generator, the standings
maths and persistence, each against a throwaway in-memory SQLite database.
