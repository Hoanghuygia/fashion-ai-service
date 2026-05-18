# Background Removal Design

## Goal
Implement a synchronous background removal API in the existing FastAPI service. The endpoint accepts an `image_id` (attachments.id), retrieves the original image from S3-compatible storage, removes the background using `rembg`, uploads a transparent PNG to a processed path, and creates a new attachment record linked to the original.

## Scope
- Add POST `/api/v1/background/remove` endpoint.
- Add background removal module with service and processor.
- Use S3-compatible storage via settings configuration.
- Create a new attachment row for the processed image and link to the original.
- Add migration for a source attachment reference column.
- Add `rembg` and `pillow` dependencies.

Out of scope: Celery integration (only structure for future jobs).

## Architecture
- `app/api/v1/background_routes.py`: thin route, request validation, and service invocation.
- `app/modules/background_removal/`:
  - `schemas.py`: request/response models.
  - `service.py`: orchestration, storage calls, db operations, error mapping.
  - `rembg_processor.py`: image loading, `rembg.remove`, PNG serialization.
- `app/infrastructure/storage/`: S3-compatible client wrapper (if not already present).
- `app/infrastructure/database/`: attachments repository (if not already present).
- `app/jobs/background_jobs.py`: placeholder for future async usage, not wired.

## Data Flow
1. Receive `image_id`.
2. Fetch attachments row by id where `is_deleted = false`.
3. Download original bytes using `bucket` + `object_key`.
4. Remove background via `rembg.remove` and serialize PNG with transparency.
5. Upload to configured bucket at key prefix `ai-fashion/clothes/processed/`.
6. Create new attachments row for processed image with:
   - `source_attachment_id` referencing original id.
   - `bucket` set to configured bucket.
   - `object_key` set to processed key.
   - `content_type` set to `image/png`.
   - `status` set to `BACKGROUND_REMOVED`.
7. Update original attachment `status` to `BACKGROUND_REMOVED`.
8. Return response payload with original and processed keys.

## Storage Details
- Bucket name is read from `settings.py` (`s3_bucket`).
- Processed path prefix: `ai-fashion/clothes/processed/`.
- Original is never overwritten.

## Error Handling
- Attachment not found or deleted: HTTP 404.
- Object missing in storage: HTTP 404.
- Invalid image bytes or PIL decode failure: HTTP 422.
- `rembg.remove` failure: HTTP 500.
- Upload failure: HTTP 502 or 500 depending on storage adapter error.

## Database Changes
- Add `source_attachment_id` (nullable) to `attachments` with a foreign key to `attachments.id`.
- Optional index on `source_attachment_id` for query efficiency.
- No edits to old migrations.

## Testing
- If the repo has established tests or scripts, add a simple test or script that exercises the service with a mocked storage adapter.
- Otherwise, skip test addition for now.

## Future Async Readiness
- Keep the service method pure and reusable so it can be called from `app/jobs/background_jobs.py` later.
- API route remains thin and can switch to enqueue jobs without changing the service contract.
