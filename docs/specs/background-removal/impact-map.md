# Background Removal — Impact Map

## Depends On

- **Internal Authentication** — the endpoint is gated by the internal credential.
- **Service Foundation** — for the response envelope, error catalog, and rate
  limiting.
- **Data Persistence** — reads the original attachment and, in a single
  transaction, creates a linked processed attachment and updates statuses
  (all-or-nothing).
- **Object storage** (system capability) — downloads the original bytes and
  uploads the processed PNG.

## Affects

- Downstream fashion features that consume processed, background-removed images:
  metadata extraction, outfit generation, and virtual try-on (all planned).
- Any consumer that relies on the `BACKGROUND_REMOVED` attachment status or the
  original-to-processed source link.

## Owned APIs

- `POST /api/v1/background/remove`.

## Key Behaviors

- Produces a transparent PNG cutout from a stored original image.
- Stores the processed image under `ai-fashion/clothes/processed/` without
  overwriting the original.
- Creates a new processed attachment linked to the original via a source
  reference.
- Sets both the original and processed attachments to `BACKGROUND_REMOVED`.
- Rejects oversized inputs by byte size and pixel count before processing.
- Executes synchronously (async execution planned).

## Change Impact

- Making processing asynchronous changes the response contract (immediate result
  vs. deferred job) and this spec's acceptance criteria; review before changing.
- Changing the processed-image key prefix or content type affects downstream
  consumers that resolve processed images.
- Changing the size/pixel limits affects the non-functional requirements and the
  `COMMON.400` error condition.
- Changing the `BACKGROUND_REMOVED` status value affects downstream features that
  branch on attachment status.
- Adding a provider abstraction (remove.bg, Clipdrop) must preserve this API
  contract and acceptance criteria, or the changes must be reflected here and in
  `api.md`.
