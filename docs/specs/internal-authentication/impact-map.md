# Internal Authentication — Impact Map

## Depends On

- **Service Foundation** — for the standardized error envelope and the
  unauthorized (`AUTH.401`) error code.

## Affects

- **Background Removal** — and every future `/api/v1` feature, all of which are
  gated by this authorization requirement.

## Owned APIs

- The `X-API-Key` credential requirement applied to all `/api/v1` endpoints.

## Key Behaviors

- Rejects unauthenticated or incorrectly authenticated requests before feature
  logic runs.
- Exempts health, root, and documentation endpoints.
- Constant-time credential comparison.

## Change Impact

- Changing the credential header name or authorization scheme affects every
  `/api/v1` feature's `api.md` and the Main Backend integration.
- Changing which endpoints are protected or exempt affects the acceptance
  criteria here and in every feature under `/api/v1`.
- Changing the unauthorized error code requires re-review of the Service
  Foundation error catalog and every feature that documents `AUTH.401`.
