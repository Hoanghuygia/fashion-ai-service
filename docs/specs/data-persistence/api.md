# Data Persistence — API Contract

## Endpoints

Data Persistence exposes no external HTTP endpoints. It provides an internal
persistence and transactional-integrity capability consumed by feature modules,
plus an operational migration contract for operators.

## Operational Contract (Migrations)

| Operation | Requirement |
|---|---|
| Upgrade to latest | Must be applied before the service handles feature requests that read or write persistent data |
| Reverse last change | Supported; a migration can be rolled back |
| Re-apply when already current | No-op; makes no changes and succeeds |

## Attachment Record

The attachments store is the shared record other features read and write. Its
externally meaningful fields:

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | string | no | Unique attachment identifier |
| `object_key` | string | no | Object-storage key of the stored bytes |
| `bucket` | string | no | Object-storage bucket |
| `original_filename` | string | yes | Original upload filename |
| `content_type` | string | yes | MIME type of the stored bytes |
| `size` | integer | yes | Size of the stored bytes |
| `status` | string | yes | Processing status set by features (e.g. `BACKGROUND_REMOVED`) |
| `source_attachment_id` | string | yes | Reference to the attachment this record was derived from |
| `is_deleted` | boolean | no | Soft-deletion flag; deleted records are excluded from active lookups |
| `created_at` | timestamp | no | Creation time |
| `updated_at` | timestamp | no | Last update time |
| `deleted_at` | timestamp | yes | Soft-deletion time |

## Transactional Guarantee

- A feature operation runs within a single transaction boundary and commits
  exactly once on success.
- Any error aborts the transaction and persists nothing from that operation.
- Active-record lookups exclude soft-deleted records.

## Validation Rules

- A record cannot be persisted without its required fields (`id`, `object_key`,
  `bucket`, `is_deleted`).
- A `source_attachment_id`, when present, references an existing attachment.

## Error Responses

Data Persistence defines no error codes of its own. Failures surface to the
calling feature, which maps them to the shared error catalog — for example
`COMMON.404` when a feature looks up a missing or deleted record, and
`INTERNAL.001` for an unexpected persistence failure.
