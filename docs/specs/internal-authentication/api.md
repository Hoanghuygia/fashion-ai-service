# Internal Authentication — API Contract

## Endpoints

Internal Authentication does not expose its own endpoints. It defines an
authorization requirement applied to all versioned feature endpoints under the
`/api/v1` prefix.

| Scope | Requirement |
|---|---|
| All `/api/v1/**` endpoints | Valid internal credential required |
| `/`, `/health`, `/docs`, `/redoc`, `/openapi.json` | No credential required |

## Request Schema

Authorization is supplied via a request header on every protected call.

| Header | Type | Required | Description |
|---|---|---|---|
| `X-API-Key` | string | yes | Shared internal credential issued to the Main Backend |

## Response Schema

Internal Authentication returns no success payload of its own. On success the
request proceeds to the target feature endpoint, which returns its own response.

## Validation Rules

- The `X-API-Key` header must be present on protected requests.
- The header value must exactly match the configured internal credential.
- Comparison is exact and constant-time; no partial or prefix match is accepted.

## Error Responses

| Status | `exceptionCode` | Condition |
|---|---|---|
| 401 | `AUTH.401` | `X-API-Key` header missing or does not match the configured credential |
