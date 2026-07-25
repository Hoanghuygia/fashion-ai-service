# Data Persistence — Impact Map

## Depends On

- No other feature. This is a base platform capability (a relational system of
  record with transactional integrity).

## Affects

- **Background Removal** — reads the original attachment and atomically creates
  a linked processed attachment while updating statuses.
- Every future feature that persists data (metadata extraction, outfit
  generation, virtual try-on, evaluation).

## Owned APIs

- The attachments record store and its persisted field and status contract.
- The single-transaction ("all-or-nothing") guarantee available to feature
  operations.
- The schema migration operational contract (upgrade to latest, reversible,
  idempotent).

## Key Behaviors

- Versioned, reversible, idempotent schema migrations.
- Multi-step operations commit exactly once and are all-or-nothing.
- Connections are validated before use.
- Active-record lookups exclude soft-deleted records.
- Record status values are stored opaquely; features own their meaning.

## Change Impact

- Adding or changing a persisted field requires a new migration and review of
  every feature that reads or writes that field, plus this spec's Attachment
  Record contract.
- Changing the transaction boundary or commit semantics affects the atomicity
  guarantee that Background Removal's "no partial success" acceptance criterion
  relies on.
- Adding a new persisted entity (e.g. metadata, outfit) requires a migration and
  its own repository; review this spec and the new feature's impact map.
- Changing the database engine or connection configuration affects deployment
  and the portability non-functional requirement.
- Removing or altering the soft-delete filter affects Background Removal's
  not-found behavior for deleted attachments.
