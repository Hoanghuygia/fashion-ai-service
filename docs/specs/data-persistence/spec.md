# Data Persistence — Specification

## Goal

Provide a durable, consistent system of record for Style Engine AI so features
can store and retrieve structured data — starting with image attachment
metadata — with guaranteed transactional integrity. Multi-step operations must
never leave partially-applied state, and schema changes must be versioned and
reversible so the service can be deployed and upgraded safely.

## Actors

- **Feature Modules** — background removal today, and future metadata, outfit,
  try-on, and evaluation features; they read and write persistent records as
  part of their operations.
- **Operators** — apply schema migrations when deploying or upgrading the
  service.
- **Attachment Consumers** — the Main Backend and downstream features that rely
  on durable, consistent attachment records and their status lifecycle.

## User Stories

- As a feature module, I can perform a multi-step data operation and be sure it
  is applied all-or-nothing, so a failure never leaves a half-written record.
- As an operator, I can bring a database to the current schema with a single,
  repeatable step so deployments are predictable.
- As an operator, I can reverse a schema change so a faulty migration can be
  rolled back.
- As an attachment consumer, I can rely on a stored attachment's identity,
  status, and source linkage remaining consistent.

## Functional Requirements

- The service persists structured records in a relational database configured
  from a single connection setting.
- The database schema is defined and evolved exclusively through versioned
  migrations; the schema is never created ad hoc at runtime.
- Each migration is reversible.
- The current schema can be applied to an empty or existing database through a
  single, idempotent "upgrade to latest" operation.
- The attachments record captures, at minimum: a unique identifier, its
  object-storage location and bucket, optional original filename, content type,
  size, a processing status, creation and update timestamps, a soft-deletion
  flag with deletion timestamp, and an optional reference to a source
  attachment.
- A business operation that spans multiple record writes is committed as a
  single transaction: either all writes persist, or none do.
- Individual data-access operations never commit on their own; the transaction
  boundary is owned by the operation, not by individual writes.
- Records marked as soft-deleted are excluded from active-record lookups.
- Status values stored on records are set and interpreted by the features that
  produce them; this foundation stores them without interpretation.

## Non-Functional Requirements

- **Reliability:** Database connections are validated before use so stale or
  broken pooled connections do not surface as request failures.
- **Integrity:** A failure at any point in a multi-step operation rolls back the
  entire operation.
- **Portability:** Schema and migrations target the supported relational engine
  and do not depend on a specific host environment.
- **Operability:** Applying migrations is safe to run repeatedly; re-running
  when already current makes no changes.
- **Security:** Database credentials come from configuration and are never
  hard-coded or logged.

## Acceptance Criteria

- Applying the "upgrade to latest" migration to an empty database creates the
  attachments store with all required fields.
- Re-running the upgrade when the database is already current makes no changes
  and reports success.
- Reversing the latest migration removes exactly what it introduced.
- A multi-step operation that fails partway leaves no records persisted from
  that operation.
- A completed multi-step operation persists all of its records atomically.
- A lookup for an active record excludes soft-deleted records.
