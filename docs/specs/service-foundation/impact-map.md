# Service Foundation — Impact Map

## Depends On

- No other feature. This is the base platform capability.

## Affects

- **Internal Authentication** — relies on the shared error catalog for its
  unauthorized response.
- **Background Removal** — relies on the shared response envelope, error catalog,
  rate limiting, and documentation surface.
- Every current and future feature that returns an API response.

## Owned APIs

- `GET /` — service metadata.
- `GET /health` — health status.
- The standardized response envelope (`data`, `message`, `stackTrace`,
  `exceptionCode`).
- The shared error-code catalog (`COMMON.400`, `AUTH.401`, `AUTH.403`,
  `COMMON.404`, `VALIDATION.001`, `RATE_LIMIT.001`, `INTERNAL.001`).

## Key Behaviors

- Uniform success and error envelope for all endpoints.
- Unauthenticated health and root checks.
- Configurable per-caller rate limiting.
- Debug-gated stack traces that never leak in production responses.

## Change Impact

- Changing the response envelope shape affects every feature's `api.md` and every
  consumer, and requires re-review of all acceptance criteria that assert on
  response fields.
- Adding, removing, or renaming an error code affects every feature that
  references that code in its `api.md` error table.
- Changing rate-limit defaults or CORS defaults affects the non-functional
  requirements here and any consumer that depends on the previous limits.
- Changing the health or root contract affects monitoring and any dependent
  health check; review this spec's acceptance criteria before altering them.
