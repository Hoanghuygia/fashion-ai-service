# Service Foundation — API Contract

## Endpoints

| Method | Path | Purpose | Authorization |
|---|---|---|---|
| GET | `/` | Report service name and status | None |
| GET | `/health` | Report service health status | None |
| GET | `/docs` | Swagger UI documentation | None |
| GET | `/redoc` | ReDoc documentation | None |
| GET | `/openapi.json` | OpenAPI schema | None |

## Standard Response Envelope

Every endpoint in the service returns this envelope. Field names use camelCase
aliases on the wire.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `data` | object \| null | yes | Payload on success; null on error |
| `message` | string | no | Human-readable outcome message |
| `stackTrace` | string \| null | yes | Present only when debug mode is enabled |
| `exceptionCode` | string \| null | yes | Stable error identifier; null on success |

## Request Schema

The root, health, and documentation endpoints take no request body or parameters.

## Response Schema

### `GET /`

Success `200`: envelope with `data`:

| Field | Type | Nullable | Description |
|---|---|---|---|
| `service` | string | no | Configured service name |
| `status` | string | no | Always `ok` |

### `GET /health`

Success `200`: envelope with `data`:

| Field | Type | Nullable | Description |
|---|---|---|---|
| `status` | string | no | Always `ok` |

## Validation Rules

- These endpoints accept no input and therefore impose no field-level validation.
- Request bodies that fail validation on any feature endpoint produce the shared
  `VALIDATION.001` error.

## Error Responses

These error identifiers form the shared catalog used across all features.

| Status | `exceptionCode` | Condition |
|---|---|---|
| 400 | `COMMON.400` | Bad request |
| 401 | `AUTH.401` | Missing or invalid authentication |
| 403 | `AUTH.403` | Forbidden |
| 404 | `COMMON.404` | Resource not found |
| 422 | `VALIDATION.001` | Request body or field validation failed |
| 429 | `RATE_LIMIT.001` | Request rate limit exceeded |
| 500 | `INTERNAL.001` | Unhandled internal error |
