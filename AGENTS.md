# Agent Notes

## Current Stack
- Python 3.12+ FastAPI service for the Style Engine AI microservice described in `README.md`.
- Implemented so far: FastAPI foundation, config, error handling, middleware, rate limiting, S3-compatible storage, `attachments` model/repo, Alembic migrations, static internal API key auth, and a synchronous background-removal module (rembg).
- Not yet implemented: async workers/job queue, provider adapter layer, pipelines/workflows, and the remaining AI modules (metadata, outfit generation, virtual try-on, evaluation).
- Local infrastructure targets PostgreSQL, Redis, and MinIO through `docker-compose.yml`.

## Commands
- Create environment and install dev dependencies: `python3 -m venv .venv && .venv/bin/python -m pip install -e ".[dev]"`
- Run tests: `.venv/bin/python -m pytest`
- Run a focused test file: `.venv/bin/python -m pytest tests/test_main.py -v`
- Lint: `.venv/bin/python -m ruff check .`
- Format: `.venv/bin/python -m ruff format .`
- Typecheck: `.venv/bin/python -m mypy app tests`
- Run API locally: `.venv/bin/python -m uvicorn app.main:app --reload`
- Apply DB migrations: `.venv/bin/python -m alembic upgrade head`
- Create a new migration: `.venv/bin/python -m alembic revision -m "message"` (use `--autogenerate` against a live DB)
- Validate Docker Compose: `docker compose config`

## Constraints
- Do not implement feature modules or API routes from the README unless explicitly requested.
- Keep provider integrations behind future abstractions; do not bind application code directly to MinIO-specific APIs.
- Do not commit secrets. Use `.env.example` for documented local defaults only.
