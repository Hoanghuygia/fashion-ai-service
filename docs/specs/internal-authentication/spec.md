# Internal Authentication — Specification

## Goal

Ensure that only the trusted Main Backend can invoke the versioned feature API of
Style Engine AI. Because the service performs expensive AI processing on behalf
of a single upstream caller, it must reject any request that does not present the
agreed internal credential.

## Actors

- **Main Backend** — the sole trusted caller, holding the shared internal
  credential.
- **Unauthorized Callers** — any other client attempting to reach versioned
  feature endpoints.

## User Stories

- As the Main Backend, I can call versioned feature endpoints by presenting the
  internal credential so my requests are accepted.
- As the service owner, I can be confident that requests without a valid
  credential are rejected before any feature logic or AI processing runs.

## Functional Requirements

- All versioned feature endpoints (under the `/api/v1` prefix) require a valid
  internal credential.
- The credential is supplied as a request header.
- A request that omits the credential is rejected as unauthorized.
- A request that presents an incorrect credential is rejected as unauthorized.
- Rejection occurs before feature logic executes.
- Health, root, and documentation endpoints are exempt and remain publicly
  reachable.

## Non-Functional Requirements

- **Security:** The credential must be compared in constant time to avoid timing
  side channels.
- **Security:** The credential must be sourced from configuration and never
  hard-coded or logged.
- **Reliability:** Authorization failures return the standardized error envelope
  with the unauthorized error code.

## Acceptance Criteria

- A request to any `/api/v1` endpoint without the credential header returns a
  `401` unauthorized error in the standard envelope.
- A request to any `/api/v1` endpoint with an incorrect credential returns a
  `401` unauthorized error in the standard envelope.
- A request with the correct credential is allowed to proceed to the feature.
- Requests to the health and root endpoints succeed without any credential.
