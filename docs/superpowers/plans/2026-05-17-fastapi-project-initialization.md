# FastAPI Project Initialization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Initialize the repository as a minimal Python 3.12+ FastAPI service foundation for later AI module implementation.

**Architecture:** Create only the service skeleton: package metadata, configuration, FastAPI app entrypoint, tests, Docker assets, and agent instructions. Do not implement metadata extraction, background removal, outfit generation, virtual try-on, provider adapters, pipelines, jobs, or business APIs.

**Tech Stack:** Python 3.12+, FastAPI, Pydantic Settings, pytest, Ruff, mypy, Docker Compose, PostgreSQL, Redis, MinIO.

---

## File Structure

- Create `pyproject.toml`: package metadata, runtime dependencies, dev dependencies, and tool configuration.
- Create `.gitignore`: Python, virtualenv, test, cache, env, and local storage ignores.
- Create `.env.example`: documented local environment variables without secrets.
- Create `app/__init__.py`: marks the application package.
- Create `app/main.py`: minimal FastAPI app with root and health endpoints only.
- Create `app/config/__init__.py`: exports settings helpers.
- Create `app/config/settings.py`: Pydantic settings for app and infrastructure config.
- Create `tests/test_main.py`: smoke tests for root and health endpoints.
- Create `Dockerfile`: container for running the FastAPI service.
- Create `docker-compose.yml`: local service dependencies and app container.
- Modify `README.md`: add concise setup and verification commands while preserving the existing architecture notes.
- Modify `AGENTS.md`: replace bare-repo notes with exact commands and current initialization constraints.

---

### Task 1: Python Project Metadata And Tooling

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "style-engine-ai"
version = "0.1.0"
description = "AI microservice for wardrobe analysis, outfit generation, virtual try-on, and outfit evaluation."
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0,<1.0.0",
    "httpx>=0.27.0,<1.0.0",
    "pydantic-settings>=2.6.0,<3.0.0",
    "sqlalchemy>=2.0.0,<3.0.0",
    "uvicorn[standard]>=0.30.0,<1.0.0",
]

[project.optional-dependencies]
dev = [
    "mypy>=1.13.0,<2.0.0",
    "pytest>=8.3.0,<9.0.0",
    "ruff>=0.8.0,<1.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["app"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
python_version = "3.12"
strict = true
plugins = []

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

- [ ] **Step 2: Create `.gitignore`**

```gitignore
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/

.venv/
venv/

.env
.env.*
!.env.example

dist/
build/
*.egg-info/

.DS_Store
```

- [ ] **Step 3: Verify tool metadata parses**

Run: `python -m tomllib pyproject.toml`

Expected: exit code 0 and no output.

---

### Task 2: Configuration Skeleton

**Files:**
- Create: `.env.example`
- Create: `app/__init__.py`
- Create: `app/config/__init__.py`
- Create: `app/config/settings.py`

- [ ] **Step 1: Create `.env.example`**

```env
APP_NAME=Style Engine AI
APP_ENV=local
DEBUG=true

DATABASE_URL=postgresql+psycopg://style_engine:style_engine@postgres:5432/style_engine
REDIS_URL=redis://redis:6379/0

STORAGE_PROVIDER=s3
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=style-engine
S3_REGION=us-east-1
S3_USE_SSL=false
S3_PATH_STYLE=true
```

- [ ] **Step 2: Create package marker files**

`app/__init__.py`:

```python
"""Style Engine AI application package."""
```

`app/config/__init__.py`:

```python
from app.config.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
```

- [ ] **Step 3: Create settings module**

```python
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Style Engine AI"
    app_env: str = "local"
    debug: bool = False

    database_url: str = Field(default="postgresql+psycopg://style_engine:style_engine@localhost:5432/style_engine")
    redis_url: str = "redis://localhost:6379/0"

    storage_provider: str = "s3"
    s3_endpoint: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_bucket: str = "style-engine"
    s3_region: str = "us-east-1"
    s3_use_ssl: bool = False
    s3_path_style: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

---

### Task 3: Minimal FastAPI Entrypoint And Tests

**Files:**
- Create: `app/main.py`
- Create: `tests/test_main.py`

- [ ] **Step 1: Write smoke tests**

```python
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_returns_service_name() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"service": "Style Engine AI", "status": "ok"}


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 2: Create minimal app**

```python
from fastapi import FastAPI

from app.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": settings.app_name, "status": "ok"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

- [ ] **Step 3: Install dependencies**

Run: `python -m venv .venv && .venv/bin/python -m pip install -e ".[dev]"`

Expected: dependencies install successfully.

- [ ] **Step 4: Run focused tests**

Run: `.venv/bin/python -m pytest tests/test_main.py -v`

Expected: 2 tests pass.

---

### Task 4: Docker Development Base

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`

- [ ] **Step 1: Create `Dockerfile`**

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app
RUN pip install --no-cache-dir -e .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Create `docker-compose.yml`**

```yaml
services:
  app:
    build: .
    env_file:
      - .env.example
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - minio

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: style_engine
      POSTGRES_USER: style_engine
      POSTGRES_PASSWORD: style_engine
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  minio:
    image: minio/minio:RELEASE.2025-04-22T22-12-26Z
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
```

- [ ] **Step 3: Validate compose config**

Run: `docker compose config`

Expected: compose file renders without errors.

---

### Task 5: Documentation And Agent Instructions

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: Add setup commands near the top of `README.md` after the overview**

```markdown
# Local Development

```bash
python -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy app tests
```

Run the API locally:

```bash
.venv/bin/python -m uvicorn app.main:app --reload
```

Run local infrastructure:

```bash
docker compose up --build
```
```

- [ ] **Step 2: Replace `AGENTS.md` with current guidance**

```markdown
# Agent Notes

## Current Stack
- Python 3.12+ FastAPI service for the Style Engine AI microservice described in `README.md`.
- Project initialization is intentionally minimal: no AI modules, provider adapters, pipelines, jobs, or business APIs are implemented yet.
- Local infrastructure targets PostgreSQL, Redis, and MinIO through `docker-compose.yml`.

## Commands
- Create environment and install dev dependencies: `python -m venv .venv && .venv/bin/python -m pip install -e ".[dev]"`
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
```

- [ ] **Step 3: Run full verification**

Run these commands:

```bash
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy app tests
docker compose config
```

Expected: all commands exit 0.
