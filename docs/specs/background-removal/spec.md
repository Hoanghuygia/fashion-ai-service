# Background Removal — Specification

## Goal

Produce a clean, transparent-background version of a previously uploaded clothing
image so downstream fashion features (metadata extraction, outfit generation,
virtual try-on) can operate on isolated garments. The feature lets the Main
Backend turn a stored original image into a processed cutout without re-uploading
the source.

## Actors

- **Main Backend** — requests background removal for a stored clothing image and
  consumes the resulting processed image reference.
- **Attachment store** — the system of record for uploaded and processed image
  metadata.
- **Object storage** — the S3-compatible store holding the original and processed
  image bytes.

## User Stories

- As the Main Backend, I can submit the identifier of an uploaded clothing image
  and receive a reference to a new transparent-background version so I can display
  or further process the garment.
- As the Main Backend, I can tell that the original image and its processed
  version are linked so I can trace one to the other.

## Functional Requirements

- The feature accepts the identifier of an existing, non-deleted uploaded image.
- The feature retrieves the original image bytes from object storage.
- The feature removes the background and produces a transparent PNG.
- The feature stores the processed image under a dedicated processed-image
  location and never overwrites the original.
- The feature records the processed image as a new attachment linked to the
  original via a source reference.
- The feature marks both the original and the processed attachment with a
  background-removed status.
- The feature returns references to both the original and processed images along
  with the resulting status.
- Processing is synchronous: the response is returned only after the processed
  image has been produced and stored. (Asynchronous execution is planned but not
  part of this contract.)

## Non-Functional Requirements

- **Security / Reliability:** The feature rejects oversized inputs before heavy
  processing to guard against decompression-bomb and oversized-image denial of
  service. Inputs are bounded by both raw byte size and decoded pixel count.
- **Authorization:** The endpoint is only reachable by an authenticated internal
  caller (see Internal Authentication).
- **Data integrity:** The original image is immutable; only new records and
  status updates are created.

## Acceptance Criteria

- Submitting a valid identifier for an existing image returns a success envelope
  containing the original object reference, the processed object reference, and a
  status of `BACKGROUND_REMOVED`.
- The processed image is stored under the processed-image location as a PNG and
  the original remains unchanged.
- A new attachment record exists for the processed image, linked to the original.
- Submitting an identifier that does not exist or refers to a deleted image
  returns a not-found error.
- Submitting an image that exceeds the configured size or pixel limits returns a
  bad-request error and no processed image is created.
- A failure during background processing returns an internal-error response and
  no partial processed record is reported as success.
