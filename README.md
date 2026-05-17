# Style Engine AI

AI microservice for wardrobe analysis, outfit generation, virtual try-on, and outfit evaluation.

---

# Overview

`style-engine-ai` is a dedicated AI service for a fashion/stylist application.

This service is responsible for:

- Clothing metadata extraction
- Background removal
- Outfit recommendation
- Virtual try-on orchestration
- Outfit evaluation/scoring
- AI pipeline orchestration
- AI provider abstraction

The system is designed with a provider-agnostic architecture, allowing easy switching between providers such as:

- OpenAI
- Google Gemini
- Replicate
- remove.bg
- Clipdrop

---

# Local Development

```bash
python3 -m venv .venv
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

Current implementation is intentionally limited to the FastAPI foundation, configuration skeleton, smoke tests, and Docker Compose infrastructure. AI modules, API routes, workers, provider adapters, pipelines, and jobs are planned architecture only.

---

# Tech Stack

| Category | Technology |
|---|---|
| Language | Python 3.12+ |
| API Framework | FastAPI |
| Task Queue | Celery or RQ |
| Cache / Queue Broker | Redis |
| Database | PostgreSQL |
| Object Storage | MinIO (S3-compatible) |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| HTTP Client | httpx |
| AI SDKs | OpenAI SDK, Google GenAI SDK |
| Containerization | Docker |
| Deployment | Docker Compose / Kubernetes-ready |

---

# Target Architecture

```text
Client
   ↓
Main Backend API
   ↓
Style Engine AI Service
   ↓
AI Providers / Models
```

The planned AI service will act as:

- AI Orchestrator
- Pipeline Processor
- Workflow Engine
- Provider Adapter Layer

---

# Core AI Modules

## 1. Metadata Extraction

Analyze clothing images and generate structured metadata.

Example output:

```json
{
  "category": "shirt",
  "color": ["white"],
  "style": ["minimal", "casual"],
  "season": ["summer"]
}
```

---

## 2. Background Removal

Remove clothing background and generate transparent PNG assets.

Supported providers:

- remove.bg
- Clipdrop
- Local models (future)

---

## 3. Outfit Generation

Generate outfit combinations based on:

- User wardrobe
- Occasion
- Weather
- Style preference
- Rule engine validation

---

## 4. Virtual Try-On

Render clothing on user images using external VTON providers.

Supported providers:

- Replicate
- Fashn.ai
- IDM-VTON (future)

---

## 5. Outfit Evaluation

Evaluate generated outfits and return:

- Compatibility score
- Color harmony
- Style explanation
- Improvement suggestions

---

# Planned Project Structure

This target structure is not fully implemented yet; it documents the intended architecture for future AI modules, routes, providers, pipelines, workflows, and jobs.

```text
style-engine-ai/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── metadata_routes.py
│   │       ├── background_routes.py
│   │       ├── outfit_routes.py
│   │       ├── tryon_routes.py
│   │       └── evaluation_routes.py
│   │
│   ├── modules/
│   │   ├── metadata/
│   │   ├── background_removal/
│   │   ├── outfit_generation/
│   │   ├── virtual_tryon/
│   │   └── outfit_evaluation/
│   │
│   ├── providers/
│   │   ├── gemini/
│   │   ├── openai/
│   │   ├── replicate/
│   │   ├── removebg/
│   │   └── clipdrop/
│   │
│   ├── pipelines/
│   │   ├── clothing_upload_pipeline.py
│   │   ├── outfit_generation_pipeline.py
│   │   ├── virtual_tryon_pipeline.py
│   │   └── outfit_scoring_pipeline.py
│   │
│   ├── workflows/
│   │   ├── process_clothing_workflow.py
│   │   └── generate_outfit_workflow.py
│   │
│   ├── jobs/
│   │   ├── celery_app.py
│   │   ├── metadata_jobs.py
│   │   ├── tryon_jobs.py
│   │   └── evaluation_jobs.py
│   │
│   ├── shared/
│   │   ├── schemas/
│   │   ├── prompts/
│   │   ├── rules/
│   │   ├── utils/
│   │   └── constants/
│   │
│   ├── infrastructure/
│   │   ├── database/
│   │   ├── storage/
│   │   ├── redis/
│   │   └── logging/
│   │
│   └── config/
│       └── settings.py
│
├── tests/
├── scripts/
├── docker/
├── docs/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# Storage Architecture

The project uses MinIO as the default object storage solution.

However, the storage layer is designed using an S3-compatible abstraction, allowing seamless migration to:

- AWS S3
- Cloudflare R2
- DigitalOcean Spaces
- Other S3-compatible storage providers

---

# Storage Design Principles

The application should never directly depend on MinIO-specific APIs.

Instead, use:

```text
Storage Interface
    ↓
S3-Compatible Client
    ↓
MinIO / AWS S3
```

This ensures future migration requires only configuration changes.

---

# Example Storage Configuration

```env
STORAGE_PROVIDER=s3

S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=style-engine
S3_REGION=us-east-1

S3_USE_SSL=false
S3_PATH_STYLE=true
```

---

# Migration to AWS S3

To migrate from MinIO to S3 later:

```env
S3_ENDPOINT=
S3_ACCESS_KEY=AWS_ACCESS_KEY
S3_SECRET_KEY=AWS_SECRET_KEY
S3_BUCKET=production-bucket
S3_REGION=ap-southeast-1

S3_USE_SSL=true
S3_PATH_STYLE=false
```

No application code changes should be required.

---

# Async Processing

AI tasks can be expensive and slow.

The planned system will use asynchronous workers for:

- Metadata extraction
- Background removal
- Virtual try-on
- Outfit scoring

Recommended flow:

```text
Upload Request
    ↓
Queue Job
    ↓
Worker Process
    ↓
Store Result
    ↓
Notify Backend
```

---

# Recommended Infrastructure

## Local Development

```text
FastAPI
Redis
PostgreSQL
MinIO
Celery Worker (planned)
```

via Docker Compose.

---

## Production

Recommended deployment:

- Kubernetes
- AWS ECS
- GCP Cloud Run
- DigitalOcean Apps Platform

---

# Design Principles

## Provider Agnostic

The intended architecture keeps AI providers swappable without affecting business logic.

---

## Pipeline-Oriented

Planned AI operations will be implemented as pipelines rather than CRUD services.

Example:

```text
Upload Clothing
→ Remove Background
→ Extract Metadata
→ Save Assets
→ Generate Embeddings
```

---

## Modular Architecture

Each planned AI capability will be isolated into its own module.

This allows:

- Independent scaling
- Easier testing
- Easier provider replacement
- Easier future fine-tuning

---

# Future Improvements

Potential future additions:

- Embedding search
- Fashion similarity search
- Personalized ranking
- Fine-tuned fashion models
- Local inference models
- Multi-modal recommendation systems
- AI stylist chat assistant
- Fashion trend analysis

---

# Initial MVP Scope

The MVP should prioritize:

- Fast iteration
- Provider APIs
- Stable architecture
- Minimal ML infrastructure complexity

Avoid training custom models initially unless necessary.

---

# Recommended Initial Providers

| Feature | Recommended Provider |
|---|---|
| Metadata | Gemini Vision |
| Background Removal | remove.bg |
| Outfit Generation | Gemini / OpenAI |
| Virtual Try-On | Replicate |
| Evaluation | Gemini Vision |

---

# License

Private project. Internal use only.
