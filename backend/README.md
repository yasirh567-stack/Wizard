# Wizard backend

FastAPI + PostgreSQL + Redis. See `../docs/SPRINT_1.md` for what this sprint
covers and `../docs/ARCHITECTURE.md` for the full system design.

## Run it

```bash
cp .env.example .env   # fill in JWT_SECRET / ENCRYPTION_KEY (see comments in the file)
docker compose up
```

That's the whole local setup — API on `:8000`, Postgres on `:5432`, Redis on
`:6379`. Migrations run automatically on container start.

- `POST /auth/register`, `POST /auth/login` — email/password auth, argon2
  hashed, JWT issued on login.
- `GET /accounts`, `GET /transactions` — require `Authorization: Bearer
  <token>`; 401 without one.
- `POST /plaid/link-token`, `POST /plaid/exchange-public-token`,
  `POST /plaid/sync/{item_id}` — Plaid Sandbox connect flow. Needs
  `PLAID_CLIENT_ID`/`PLAID_SECRET` in `.env` (free at
  https://dashboard.plaid.com); everything else works without them.

## Tests

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest
```

Tests run against in-memory SQLite, not the dev Postgres — no external
service needed. This works because every model uses `app/db/types.py`'s
`GUID` type (Postgres's native `UUID` in production, a portable `CHAR(32)`
elsewhere) instead of the Postgres-only column type directly, so the same
model definitions are valid on both.

## Migrations

```bash
docker compose run --rm api alembic revision --autogenerate -m "message"
docker compose run --rm api alembic upgrade head
```
