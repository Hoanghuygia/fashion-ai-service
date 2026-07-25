# Background Removal — API Contract

## Endpoints

| Method | Path | Purpose | Authorization |
|---|---|---|---|
| POST | `/api/v1/background/remove` | Remove the background from a stored image and produce a transparent PNG | Internal credential required (`X-API-Key`) |

## Request Schema

Body (JSON):

| Field | Type | Required | Constraints |
|---|---|---|---|
| `image_id` | string | yes | Identifier of an existing, non-deleted attachment |

## Response Schema

Success `200`: standard envelope with `data`:

| Field | Type | Nullable | Description |
|---|---|---|---|
| `image_id` | string | no | Identifier of the original image |
| `original_object_key` | string | no | Object-storage key of the original image |
| `processed_object_key` | string | no | Object-storage key of the processed PNG |
| `status` | string | no | Always `BACKGROUND_REMOVED` on success |

The processed image is stored under the `ai-fashion/clothes/processed/`
key prefix as a PNG (`image/png`).

## Validation Rules

- `image_id` is required; a missing or malformed body yields `VALIDATION.001`.
- The referenced attachment must exist and must not be deleted.
- The source image must not exceed the configured maximum raw byte size or
  decoded pixel count.

## Error Responses

| Status | `exceptionCode` | Condition |
|---|---|---|
| 401 | `AUTH.401` | Missing or invalid internal credential |
| 404 | `COMMON.404` | `image_id` does not exist or refers to a deleted attachment |
| 400 | `COMMON.400` | Source image exceeds the size or pixel limit |
| 422 | `VALIDATION.001` | Request body failed validation (e.g. missing `image_id`) |
| 429 | `RATE_LIMIT.001` | Request rate limit exceeded |
| 500 | `INTERNAL.001` | Background removal failed during processing or storage |
