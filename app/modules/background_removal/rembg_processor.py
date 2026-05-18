from __future__ import annotations

from io import BytesIO

from PIL import Image


class RembgProcessor:
    def remove_background(self, data: bytes) -> bytes:
        from rembg import remove  # type: ignore[import-untyped]

        image = Image.open(BytesIO(data)).convert("RGBA")
        output = remove(image)
        buffer = BytesIO()
        output.save(buffer, format="PNG")
        return buffer.getvalue()
