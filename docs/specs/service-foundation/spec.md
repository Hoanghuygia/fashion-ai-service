# Service Foundation — Specification

## Goal

Provide the baseline HTTP service platform for Style Engine AI so that every
feature exposes a consistent, observable, and safely-limited API surface. This
foundation exists so client systems (primarily the Main Backend) can verify the
service is alive and can rely on a uniform response and error format across all
features.

## Actors

- **Main Backend** — the trusted upstream service that calls Style Engine AI.
- **Operators / Monitoring** — infrastructure and health-check probes that
  verify service availability.
- **API Consumers** — any authorized caller of feature endpoints that depends on
  the shared response and error contract.

## User Stories

- As monitoring, I can call a health endpoint and receive a stable success
  response so I can confirm the service is running.
- As an API consumer, I receive every response in a single predictable envelope
  so I can parse success and error results uniformly.
- As an operator, I can rely on the service rejecting excessive request volume so
  a single caller cannot overwhelm it.

## Functional Requirements

- The service exposes a root endpoint that reports the service name and an `ok`
  status.
- The service exposes a health endpoint that reports an `ok` status.
- The root and health endpoints are reachable without authentication.
- Every response — success or error — is returned in one standardized envelope
  containing `data`, `message`, `stackTrace`, and `exceptionCode` fields.
- Successful responses carry the payload in `data` with a human-readable
  `message` and null error fields.
- Error responses carry a null `data`, a `message`, a stable `exceptionCode`,
  and an optional `stackTrace`.
- Interactive API documentation (OpenAPI schema, Swagger UI, ReDoc) is available
  for the service.

## Non-Functional Requirements

- **Reliability:** The health and root endpoints must remain available and cheap,
  performing no external I/O.
- **Consistency:** All features must use the shared response envelope and the
  shared catalog of error codes; no feature defines its own ad-hoc error shape.
- **Rate limiting:** The service limits request volume per caller within a
  configurable time window and rejects excess requests with a rate-limit error.
- **Cross-origin access:** The service permits configured browser origins via
  CORS, defaulting to local development origins.
- **Diagnostics:** Stack traces are included in error responses only when debug
  mode is enabled; they are never exposed in production responses.

## Acceptance Criteria

- Calling the root endpoint returns a success envelope whose `data` contains the
  service name and `status` of `ok`.
- Calling the health endpoint returns a success envelope whose `data` contains a
  `status` of `ok`.
- A malformed request to any endpoint returns the standardized error envelope
  with the validation error code and no leaked stack trace when debug is off.
- Exceeding the configured request rate returns the standardized error envelope
  with the rate-limit error code.
- The OpenAPI schema and documentation endpoints are reachable.
