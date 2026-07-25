# Agent Notes

## Project Overview
- `style-engine-ai` is a Python 3.12+ FastAPI microservice for a fashion/stylist
  application. It provides AI capabilities: clothing metadata extraction,
  background removal, outfit generation, virtual try-on, and outfit evaluation.
  See `README.md` for the full product vision.
- The service is designed provider-agnostic: AI providers (OpenAI, Gemini,
  Replicate, remove.bg, Clipdrop) are meant to sit behind adapter abstractions
  so they can be swapped without touching business logic.

## Current Stack
- Implemented so far: FastAPI foundation, config (`app/config`), error handling
  and exceptions (`app/core`), middleware and rate limiting, S3-compatible
  storage client, `attachments` model/repository, Alembic migrations, static
  internal API key auth (`app/core/auth.py`), and a synchronous
  background-removal module (rembg).
- Not yet implemented: async workers/job queue, provider adapter layer,
  pipelines/workflows, and the remaining AI modules (metadata, outfit
  generation, virtual try-on, evaluation). These are documented as intended
  architecture in `README.md`, not current code.
- Local infrastructure targets PostgreSQL, Redis, and MinIO through
  `docker-compose.yml`.

## Module Organization & Architecture Boundaries
- `app/main.py` — FastAPI app assembly and router registration.
- `app/api/v1/` — HTTP routes. Routes wire dependencies and translate
  domain/service errors into `AppException`s; they hold no business logic.
- `app/modules/<feature>/` — self-contained feature modules (e.g.
  `background_removal`) with `service.py`, `schemas.py`, and processing code.
  Services depend on infrastructure through `Protocol` interfaces defined
  locally, not on concrete infrastructure classes.
- `app/core/` — cross-cutting concerns: `auth.py`, `exceptions.py`,
  `error_codes.py`, `responses.py` (`BaseResponse`/`success_response`),
  `middleware.py`, `lifespan.py`.
- `app/infrastructure/` — external-system adapters: `database/` (SQLAlchemy
  models, repositories, session), `storage/` (S3-compatible client).
- `app/config/settings.py` — pydantic-settings configuration; access via
  `get_settings`.
- `migrations/` — Alembic migrations (`alembic.ini` at repo root).
- Keep the dependency direction `api → modules → infrastructure`. Do not import
  API/route code from modules or infrastructure.

## Commands
Use `.venv/Scripts/python` on Windows; `.venv/bin/python` on macOS/Linux.
- Create environment and install dev dependencies: `python -m venv .venv && .venv/Scripts/python -m pip install -e ".[dev]"`
- Run tests: `.venv/Scripts/python -m pytest`
- Run a focused test file: `.venv/Scripts/python -m pytest tests/test_main.py -v`
- Lint: `.venv/Scripts/python -m ruff check .`
- Format: `.venv/Scripts/python -m ruff format .`
- Typecheck: `.venv/Scripts/python -m mypy app tests`
- Run API locally: `.venv/Scripts/python -m uvicorn app.main:app --reload`
- Apply DB migrations: `.venv/Scripts/python -m alembic upgrade head`
- Create a new migration: `.venv/Scripts/python -m alembic revision -m "message"` (use `--autogenerate` against a live DB)
- Validate Docker Compose: `docker compose config`

## Coding Conventions
- Ruff enforces formatting and lint; line length is 100, target `py312`, lint
  rules `E, F, I, UP, B`. Run `ruff format` before committing.
- mypy runs in `strict` mode over `app` and `tests` — annotate all signatures,
  including test helpers.
- Prefer `Protocol` interfaces for dependencies that cross module boundaries
  (see `app/modules/background_removal/service.py`) so implementations stay
  swappable and testable.
- API responses use `BaseResponse[...]` via `success_response`; surface failures
  as `AppException(ErrorCode.*, "message")` rather than raw HTTP exceptions.
- Compare secrets in constant time (`secrets.compare_digest`), as in
  `app/core/auth.py`.

## Testing Expectations
- Tests live in `tests/`, run with pytest (`testpaths = ["tests"]`,
  `pythonpath = ["."]`).
- Add or update tests alongside behavior changes; mirror the existing
  Protocol-based fakes to test services without live infrastructure (see
  `tests/test_background_removal_service.py`).
- Before finishing a change, run the test, ruff, and mypy commands above.

## Constraints
- Do not implement feature modules or API routes from the README unless
  explicitly requested.
- Keep provider integrations behind future abstractions; do not bind application
  code directly to MinIO-specific APIs (use the S3-compatible client).
- Do not commit secrets. Use `.env.example` for documented local defaults only.

## Specification System
This repository is intended to follow a specification-first layout. The expected
paths are:

```text
docs/
├── architecture/
│   └── dependency-map.md
└── specs/
    └── <feature>/
        ├── spec.md
        ├── api.md
        └── impact-map.md
```

Each file's role:
- `docs/specs/<feature>/spec.md` — business requirements and acceptance criteria.
- `docs/specs/<feature>/api.md` — external API contracts.
- `docs/specs/<feature>/impact-map.md` — feature-level dependencies and change
  impact.
- `docs/architecture/dependency-map.md` — high-level relationships between
  features.

Before starting a task, agents should:
1. Identify the feature or domain the task affects.
2. Find the matching directory under `docs/specs/<feature>/`.
3. Read `spec.md`, `api.md`, and `impact-map.md` when present.
4. Read `docs/architecture/dependency-map.md` when present to understand
   high-level feature relationships.
5. Use existing repository terminology; do not create a second specification for
   a feature that already has one.
6. Report missing specification guidance instead of assuming undocumented
   business rules, API contracts, dependencies, or architecture decisions.

Current status of these paths:
- `docs/architecture/dependency-map.md` exists and lists the implemented
  features and their relationships.
- `docs/specs/` contains specifications for the implemented features:
  `service-foundation`, `internal-authentication`, and `background-removal`.
- The former `docs/superpowers/` implementation plans have been migrated into
  these specifications and removed.
- When specifications need to be created or maintained, use the `spec-writer`
  skill; do not scaffold or invent spec content here.
