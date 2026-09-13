# Agent guide

LeagueTable is a scoreboard for one amateur sports league across several
seasons. Read `_docs/specs.md` before changing behaviour.

## Layout

- `frontend/` – React + Vite, plain JavaScript.
- `backend/` – FastAPI managed with `uv`.
- `openapi.yaml` – the API contract. It is the source of truth; change it first,
  then the backend, then the frontend.

## Rules

- Keep every backend call in `frontend/src/api.js`. Components never call
  `fetch` directly.
- The backend reads its database URL from the `DATABASE_URL` environment
  variable and falls back to local SQLite. Never hard-code a driver elsewhere.
- Browser origins come from `CORS_ORIGINS`. Never hard-code a host or port in
  the middleware.
- Uniqueness is enforced by database constraints, not by a read followed by a
  write. Translate `IntegrityError` into a conflict instead.
- Standings are always computed from matches, never stored.
- Write or update tests in `backend/tests/` for any endpoint you touch, and run
  them before reporting the work as done.
- English for code, comments, documentation and commit messages.

## Commands

```bash
# backend
cd backend && uv sync && uv run uvicorn app.main:app --reload
cd backend && uv run pytest

# frontend
cd frontend && npm install && npm run dev
```
