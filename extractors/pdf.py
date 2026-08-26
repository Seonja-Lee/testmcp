from pathlib import Path

from pypdf import PdfReader


def extract_pdf(path: Path, max_pages: int, max_chars: int) -> str:
    reader = PdfReader(str(path))
    total_pages = len(reader.pages)
    pages_to_read = min(total_pages, max_pages)

    parts = [f"[PDF] {path.name} - 총 {total_pages}페이지 중 {pages_to_read}페이지 추출"]
    char_count = 0
    truncated_by_chars = False

    for i in range(pages_to_read):
        text = (reader.pages[i].extract_text() or "").strip()
        remaining = max_chars - char_count
        if remaining <= 0:
            truncated_by_chars = True
            break
        if len(text) > remaining:
            text = text[:remaining]
            truncated_by_chars = True
        parts.append(f"\n--- Page {i + 1} ---\n{text}")
        char_count += len(text)
        if truncated_by_chars:
            break

    if truncated_by_chars:
        parts.append(f"\n[문자 수 제한({max_chars})으로 이후 내용 생략]")
    elif pages_to_read < total_pages:
        parts.append(f"\n[페이지 수 제한({max_pages})으로 이후 {total_pages - pages_to_read}페이지 생략]")

    return "\n".join(parts)
