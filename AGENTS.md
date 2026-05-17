# Agent Notes

## Current Stack
- Python 3.12+ FastAPI service for the Style Engine AI microservice described in `README.md`.
- Project initialization is intentionally minimal: no AI modules, provider adapters, pipelines, jobs, or business APIs are implemented yet.
- Local infrastructure targets PostgreSQL, Redis, and MinIO through `docker-compose.yml`.

## Commands
- Create environment and install dev dependencies: `python3 -m venv .venv && .venv/bin/python -m pip install -e ".[dev]"`
- Run tests: `.venv/bin/python -m pytest`
- Run a focused test file: `.venv/bin/python -m pytest tests/test_main.py -v`
- Lint: `.venv/bin/python -m ruff check .`
- Format: `.venv/bin/python -m ruff format .`
- Typecheck: `.venv/bin/python -m mypy app tests`
- Run API locally: `.venv/bin/python -m uvicorn app.main:app --reload`
- Validate Docker Compose: `docker compose config`

## Constraints
- Do not implement feature modules or API routes from the README unless explicitly requested.
- Keep provider integrations behind future abstractions; do not bind application code directly to MinIO-specific APIs.
- Do not commit secrets. Use `.env.example` for documented local defaults only.
