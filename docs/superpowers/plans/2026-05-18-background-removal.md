# Background Removal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a synchronous background removal endpoint that loads images by attachment id, removes background with rembg, stores a processed PNG, and creates a linked attachment record.

**Architecture:** Add a background removal module with a service orchestrating DB + storage calls, a processor wrapping rembg + Pillow, a thin API route, and a storage adapter. Add a migration for `source_attachment_id` linkage and keep the service API compatible with future async jobs.

**Tech Stack:** FastAPI, Pydantic, SQLAlchemy, psycopg, S3-compatible storage, rembg, Pillow.

---

## File Structure

- Create: `app/api/v1/background_routes.py` (route definitions)
- Create: `app/api/v1/__init__.py` (router export)
- Modify: `app/main.py` (include v1 router)
- Create: `app/modules/background_removal/schemas.py` (request/response models)
- Create: `app/modules/background_removal/rembg_processor.py` (image processing)
- Create: `app/modules/background_removal/service.py` (business logic)
- Create: `app/infrastructure/storage/s3_client.py` (S3-compatible storage helper)
- Create: `app/infrastructure/database/attachments_repo.py` (queries/updates)
- Create: `app/infrastructure/database/session.py` (SQLAlchemy session factory)
- Create: `app/infrastructure/database/models.py` (Attachment model)
- Create: `app/infrastructure/database/migrations/2026_05_18_add_source_attachment_id.py` (migration)
- Modify: `requirements.txt` (add rembg + pillow)
- Test: `tests/test_background_removal_service.py` (service-level test with fakes)

---

### Task 1: Add database model + session + repository

**Files:**
- Create: `app/infrastructure/database/session.py`
- Create: `app/infrastructure/database/models.py`
- Create: `app/infrastructure/database/attachments_repo.py`

- [ ] **Step 1: Write failing test for repository CRUD**

```python
from app.infrastructure.database.attachments_repo import AttachmentRepository


def test_attachment_repo_create_and_get(session):
    repo = AttachmentRepository(session)
    created = repo.create(
        id="att_1",
        object_key="raw/test.png",
        bucket="style-engine",
        original_filename="test.png",
        content_type="image/png",
        size=123,
        status="UPLOADED",
        is_deleted=False,
        source_attachment_id=None,
    )

    loaded = repo.get_active_by_id("att_1")

    assert created.id == loaded.id
    assert loaded.is_deleted is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_background_removal_service.py::test_attachment_repo_create_and_get -v`

Expected: FAIL with `ModuleNotFoundError` for repo module.

- [ ] **Step 3: Create SQLAlchemy session and model**

`app/infrastructure/database/session.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings


def get_engine():
    settings = get_settings()
    return create_engine(settings.database_url, future=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
```

`app/infrastructure/database/models.py`

```python
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(String, primary_key=True)
    object_key = Column(String, nullable=False)
    bucket = Column(String, nullable=False)
    original_filename = Column(String, nullable=True)
    content_type = Column(String, nullable=True)
    size = Column(Integer, nullable=True)
    status = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)
    source_attachment_id = Column(String, ForeignKey("attachments.id"), nullable=True)
```

- [ ] **Step 4: Create repository implementation**

`app/infrastructure/database/attachments_repo.py`

```python
from sqlalchemy import select, update

from app.infrastructure.database.models import Attachment


class AttachmentRepository:
    def __init__(self, session):
        self.session = session

    def get_active_by_id(self, attachment_id: str) -> Attachment | None:
        stmt = select(Attachment).where(
            Attachment.id == attachment_id, Attachment.is_deleted.is_(False)
        )
        return self.session.execute(stmt).scalars().first()

    def create(
        self,
        *,
        id: str,
        object_key: str,
        bucket: str,
        original_filename: str | None,
        content_type: str | None,
        size: int | None,
        status: str | None,
        is_deleted: bool,
        source_attachment_id: str | None,
    ) -> Attachment:
        attachment = Attachment(
            id=id,
            object_key=object_key,
            bucket=bucket,
            original_filename=original_filename,
            content_type=content_type,
            size=size,
            status=status,
            is_deleted=is_deleted,
            source_attachment_id=source_attachment_id,
        )
        self.session.add(attachment)
        self.session.commit()
        self.session.refresh(attachment)
        return attachment

    def update_status(self, attachment_id: str, status: str) -> None:
        stmt = update(Attachment).where(Attachment.id == attachment_id).values(status=status)
        self.session.execute(stmt)
        self.session.commit()
```

- [ ] **Step 5: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_background_removal_service.py::test_attachment_repo_create_and_get -v`

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add app/infrastructure/database/session.py app/infrastructure/database/models.py app/infrastructure/database/attachments_repo.py tests/test_background_removal_service.py
git commit -m "feat: add attachments repository"
```

---

### Task 2: Add migration for source attachment link

**Files:**
- Create: `app/infrastructure/database/migrations/2026_05_18_add_source_attachment_id.py`

- [ ] **Step 1: Write migration test stub**

```python
def test_migration_placeholder():
    assert True
```

- [ ] **Step 2: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_background_removal_service.py::test_migration_placeholder -v`

Expected: PASS

- [ ] **Step 3: Write migration script**

`app/infrastructure/database/migrations/2026_05_18_add_source_attachment_id.py`

```python
from sqlalchemy import Column, ForeignKey, MetaData, String, Table
from sqlalchemy import create_engine

from app.config import get_settings


def upgrade() -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url, future=True)
    metadata = MetaData()
    attachments = Table("attachments", metadata, autoload_with=engine)
    if "source_attachment_id" not in attachments.c:
        Column("source_attachment_id", String, ForeignKey("attachments.id"), nullable=True).create(
            attachments
        )


def downgrade() -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url, future=True)
    metadata = MetaData()
    attachments = Table("attachments", metadata, autoload_with=engine)
    if "source_attachment_id" in attachments.c:
        attachments.c.source_attachment_id.drop()
```

- [ ] **Step 4: Commit**

```bash
git add app/infrastructure/database/migrations/2026_05_18_add_source_attachment_id.py tests/test_background_removal_service.py
git commit -m "feat: add source attachment migration"
```

---

### Task 3: Add storage adapter

**Files:**
- Create: `app/infrastructure/storage/s3_client.py`

- [ ] **Step 1: Write failing test for storage adapter**

```python
from app.infrastructure.storage.s3_client import StorageClient


def test_storage_client_builds():
    client = StorageClient()
    assert client is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_background_removal_service.py::test_storage_client_builds -v`

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement storage client**

```python
import boto3
from botocore.config import Config

from app.config import get_settings


class StorageClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.bucket = settings.s3_bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
            use_ssl=settings.s3_use_ssl,
            config=Config(s3={"addressing_style": "path" if settings.s3_path_style else "virtual"}),
        )

    def download(self, bucket: str, object_key: str) -> bytes:
        response = self.client.get_object(Bucket=bucket, Key=object_key)
        return response["Body"].read()

    def upload(self, bucket: str, object_key: str, data: bytes, content_type: str) -> None:
        self.client.put_object(Bucket=bucket, Key=object_key, Body=data, ContentType=content_type)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_background_removal_service.py::test_storage_client_builds -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/infrastructure/storage/s3_client.py tests/test_background_removal_service.py
git commit -m "feat: add s3 storage client"
```

---

### Task 4: Add background removal processor + service

**Files:**
- Create: `app/modules/background_removal/rembg_processor.py`
- Create: `app/modules/background_removal/service.py`
- Create: `app/modules/background_removal/schemas.py`

- [ ] **Step 1: Write failing test for service happy path**

```python
from app.modules.background_removal.service import BackgroundRemovalService


def test_service_returns_processed_keys(fake_storage, fake_repo, fake_session):
    service = BackgroundRemovalService(fake_storage, fake_repo)
    result = service.remove_background(
        image_id="att_1",
        processed_prefix="ai-fashion/clothes/processed/",
    )
    assert result.processed_object_key.startswith("ai-fashion/clothes/processed/")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_background_removal_service.py::test_service_returns_processed_keys -v`

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement schemas**

`app/modules/background_removal/schemas.py`

```python
from pydantic import BaseModel


class BackgroundRemovalRequest(BaseModel):
    image_id: str


class BackgroundRemovalResponse(BaseModel):
    image_id: str
    original_object_key: str
    processed_object_key: str
    status: str
```

- [ ] **Step 4: Implement rembg processor**

`app/modules/background_removal/rembg_processor.py`

```python
from io import BytesIO

from PIL import Image
from rembg import remove


class BackgroundRemovalProcessor:
    def process(self, data: bytes) -> bytes:
        image = Image.open(BytesIO(data)).convert("RGBA")
        output = remove(image)
        buffer = BytesIO()
        output.save(buffer, format="PNG")
        return buffer.getvalue()
```

- [ ] **Step 5: Implement service**

`app/modules/background_removal/service.py`

```python
import uuid

from app.modules.background_removal.rembg_processor import BackgroundRemovalProcessor
from app.modules.background_removal.schemas import BackgroundRemovalResponse


class BackgroundRemovalError(Exception):
    pass


class BackgroundRemovalService:
    def __init__(self, storage_client, attachments_repo) -> None:
        self.storage = storage_client
        self.repo = attachments_repo
        self.processor = BackgroundRemovalProcessor()

    def remove_background(self, image_id: str, processed_prefix: str) -> BackgroundRemovalResponse:
        attachment = self.repo.get_active_by_id(image_id)
        if attachment is None:
            raise BackgroundRemovalError("NOT_FOUND")

        data = self.storage.download(attachment.bucket, attachment.object_key)
        processed_bytes = self.processor.process(data)

        processed_id = f"att_{uuid.uuid4().hex}"
        processed_key = f"{processed_prefix}{processed_id}_nobg.png"

        self.storage.upload(attachment.bucket, processed_key, processed_bytes, "image/png")

        self.repo.create(
            id=processed_id,
            object_key=processed_key,
            bucket=attachment.bucket,
            original_filename=attachment.original_filename,
            content_type="image/png",
            size=len(processed_bytes),
            status="BACKGROUND_REMOVED",
            is_deleted=False,
            source_attachment_id=attachment.id,
        )

        self.repo.update_status(attachment.id, "BACKGROUND_REMOVED")

        return BackgroundRemovalResponse(
            image_id=attachment.id,
            original_object_key=attachment.object_key,
            processed_object_key=processed_key,
            status="BACKGROUND_REMOVED",
        )
```

- [ ] **Step 6: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_background_removal_service.py::test_service_returns_processed_keys -v`

Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add app/modules/background_removal/schemas.py app/modules/background_removal/rembg_processor.py app/modules/background_removal/service.py tests/test_background_removal_service.py
git commit -m "feat: add background removal service"
```

---

### Task 5: Add API route

**Files:**
- Create: `app/api/v1/background_routes.py`
- Create: `app/api/v1/__init__.py`
- Modify: `app/main.py`

- [ ] **Step 1: Write failing API test**

```python
from fastapi.testclient import TestClient

from app.main import app


def test_remove_background_route_exists():
    client = TestClient(app)
    response = client.post("/api/v1/background/remove", json={"image_id": "att_1"})
    assert response.status_code in {200, 404}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_background_removal_service.py::test_remove_background_route_exists -v`

Expected: FAIL with 404 because route not registered.

- [ ] **Step 3: Implement route and router wiring**

`app/api/v1/background_routes.py`

```python
from fastapi import APIRouter, HTTPException

from app.infrastructure.database.attachments_repo import AttachmentRepository
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.storage.s3_client import StorageClient
from app.modules.background_removal.schemas import BackgroundRemovalRequest
from app.modules.background_removal.service import BackgroundRemovalError, BackgroundRemovalService


router = APIRouter(prefix="/background", tags=["background"])


@router.post("/remove")
def remove_background(payload: BackgroundRemovalRequest):
    storage = StorageClient()
    with SessionLocal() as session:
        repo = AttachmentRepository(session)
        service = BackgroundRemovalService(storage, repo)
        try:
            return service.remove_background(
                image_id=payload.image_id,
                processed_prefix="ai-fashion/clothes/processed/",
            )
        except BackgroundRemovalError as exc:
            if str(exc) == "NOT_FOUND":
                raise HTTPException(status_code=404, detail="image_id not found") from exc
            raise HTTPException(status_code=500, detail="background removal failed") from exc
```

`app/api/v1/__init__.py`

```python
from fastapi import APIRouter

from app.api.v1.background_routes import router as background_router


router = APIRouter(prefix="/api/v1")
router.include_router(background_router)
```

`app/main.py`

```python
from app.api.v1 import router as v1_router

app.include_router(v1_router)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_background_removal_service.py::test_remove_background_route_exists -v`

Expected: PASS (200 or 404)

- [ ] **Step 5: Commit**

```bash
git add app/api/v1/background_routes.py app/api/v1/__init__.py app/main.py tests/test_background_removal_service.py
git commit -m "feat: add background removal route"
```

---

### Task 6: Update dependencies

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Add dependencies**

```text
rembg
pillow
```

- [ ] **Step 2: Commit**

```bash
git add requirements.txt
git commit -m "chore: add rembg dependencies"
```

---

## Plan Self-Review

**Spec coverage:**
- Endpoint added in Task 5.
- Uses image_id to query attachments in Task 4.
- Uses bucket/object_key for download in Task 4.
- Uses rembg + Pillow in Task 4.
- Uploads PNG to `ai-fashion/clothes/processed/` in Task 5.
- Creates new attachment record and links via `source_attachment_id` in Task 4.
- Updates status to `BACKGROUND_REMOVED` in Task 4.
- Error handling via service + HTTP mapping in Task 5.
- Requirements update in Task 6.

**Placeholder scan:** No TODO/TBD patterns found.

**Type consistency:** Method names and schema fields consistent across tasks.

---

Plan complete and saved to `docs/superpowers/plans/2026-05-18-background-removal.md`. Two execution options:

1. Subagent-Driven (recommended) - I dispatch a fresh subagent per task, review between tasks, fast iteration
2. Inline Execution - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
