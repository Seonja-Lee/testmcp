from io import BytesIO
from pathlib import Path

from PIL import Image as PILImage

from mcp.server.mcpserver.utilities.types import Image

MAX_DIMENSION = 1600


def extract_image(path: Path) -> tuple[str, Image]:
    with PILImage.open(path) as im:
        width, height = im.size
        mode = im.mode
        original_format = im.format or path.suffix.lstrip(".").upper() or "PNG"

        save_format = "JPEG" if original_format.upper() == "JPEG" else "PNG"
        resized = im
        if max(width, height) > MAX_DIMENSION:
            scale = MAX_DIMENSION / max(width, height)
            new_size = (max(1, int(width * scale)), max(1, int(height * scale)))
            resized = im.resize(new_size)

        if save_format == "JPEG" and resized.mode in ("RGBA", "P"):
            resized = resized.convert("RGB")

        buf = BytesIO()
        resized.save(buf, format=save_format)

        meta = f"[Image] {path.name} - {width}x{height}, mode={mode}, format={original_format}"
        return meta, Image(data=buf.getvalue(), format=save_format.lower())
