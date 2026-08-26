from io import BytesIO
from pathlib import Path

from mcp.server.mcpserver.utilities.types import Image


def extract_svg(path: Path, max_chars: int) -> tuple[str, Image | None]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    if len(raw) > max_chars:
        raw = raw[:max_chars] + f"\n[문자 수 제한({max_chars})으로 생략]"
    text_part = f"[SVG] {path.name}\n{raw}"

    image = None
    try:
        from reportlab.graphics import renderPM
        from svglib.svglib import svg2rlg

        drawing = svg2rlg(str(path))
        if drawing is not None:
            buf = BytesIO()
            renderPM.drawToFile(drawing, buf, fmt="PNG")
            image = Image(data=buf.getvalue(), format="png")
    except Exception:
        # 래스터화에 실패해도 원문 텍스트는 그대로 반환한다.
        image = None

    return text_part, image
