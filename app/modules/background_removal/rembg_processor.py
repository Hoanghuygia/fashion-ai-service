from __future__ import annotations

from io import BytesIO

from PIL import Image

# Guardrails against decompression-bomb / oversized-image DoS.
# A small crafted file can declare huge dimensions in its header, so we reject
# on both raw byte size and decoded pixel count before doing any heavy work.
MAX_IMAGE_BYTES = 15 * 1024 * 1024  # 15 MB
MAX_IMAGE_PIXELS = 40_000_000  # 40 megapixels

# Backstop: make Pillow itself raise DecompressionBombError past this limit.
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS


class ImageTooLargeError(Exception):
    pass


class RembgProcessor:
    def __init__(
        self,
        max_bytes: int = MAX_IMAGE_BYTES,
        max_pixels: int = MAX_IMAGE_PIXELS,
    ) -> None:
        self.max_bytes = max_bytes
        self.max_pixels = max_pixels

    def remove_background(self, data: bytes) -> bytes:
        if len(data) > self.max_bytes:
            raise ImageTooLargeError(
                f"Image is {len(data)} bytes, exceeds limit of {self.max_bytes} bytes"
            )

        from rembg import remove  # type: ignore[import-untyped]

        with Image.open(BytesIO(data)) as image:
            width, height = image.size
            if width * height > self.max_pixels:
                raise ImageTooLargeError(
                    f"Image is {width}x{height} px, exceeds limit of {self.max_pixels} px"
                )
            rgba = image.convert("RGBA")

        output = remove(rgba)
        buffer = BytesIO()
        output.save(buffer, format="PNG")
        return buffer.getvalue()
