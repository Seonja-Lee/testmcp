import json
from pathlib import Path

from mcp.server.mcpserver import MCPServer

from extractors import PathError, resolve_path
from extractors.docx import extract_docx
from extractors.image import extract_image
from extractors.pdf import extract_pdf
from extractors.pptx import extract_pptx
from extractors.svg import extract_svg

mcp = MCPServer("file-analysis-mcp")

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}
SUPPORTED_EXTENSIONS = {".pdf", ".pptx", ".docx", ".svg"} | IMAGE_EXTENSIONS


@mcp.tool()
def list_folder_structure(path: str, max_depth: int = 5) -> str:
    """지정한 폴더를 재귀적으로 탐색해 트리 구조, 확장자별 파일 개수, 총 용량을 JSON 문자열로 반환한다."""
    try:
        root = resolve_path(path)
    except PathError as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

    if not root.is_dir():
        return json.dumps({"error": f"폴더가 아닙니다: {root}"}, ensure_ascii=False)

    ext_counts: dict[str, int] = {}
    total_files = 0
    total_size = 0

    def walk(dir_path: Path, depth: int) -> dict:
        nonlocal total_files, total_size
        node: dict = {"name": dir_path.name or str(dir_path), "type": "directory", "children": []}

        if depth > max_depth:
            node["truncated"] = True
            return node

        try:
            entries = sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except PermissionError:
            node["error"] = "접근 권한 없음"
            return node

        for entry in entries:
            if entry.is_dir():
                node["children"].append(walk(entry, depth + 1))
                continue
            try:
                size = entry.stat().st_size
            except OSError:
                size = 0
            ext = entry.suffix.lower() or "(no ext)"
            ext_counts[ext] = ext_counts.get(ext, 0) + 1
            total_files += 1
            total_size += size
            node["children"].append(
                {
                    "name": entry.name,
                    "type": "file",
                    "extension": ext,
                    "size_bytes": size,
                    "supported": ext in SUPPORTED_EXTENSIONS,
                }
            )
        return node

    tree = walk(root, 0)
    result = {
        "root": str(root),
        "total_files": total_files,
        "total_size_bytes": total_size,
        "extension_counts": ext_counts,
        "tree": tree,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def read_document(path: str, max_chars: int = 20000, max_pages: int = 30) -> list:
    """지정한 문서 파일(PDF, PPTX, DOCX, SVG, 이미지)의 내용을 읽어 텍스트/이미지로 반환한다.
    반환된 텍스트/이미지를 바탕으로 호출자가 직접 요약을 수행해야 한다."""
    try:
        file_path = resolve_path(path)
    except PathError as e:
        return [f"오류: {e}"]

    if not file_path.is_file():
        return [f"오류: 파일이 아닙니다: {file_path}"]

    ext = file_path.suffix.lower()

    try:
        if ext == ".pdf":
            return [extract_pdf(file_path, max_pages=max_pages, max_chars=max_chars)]
        if ext == ".pptx":
            return [extract_pptx(file_path, max_chars=max_chars)]
        if ext == ".docx":
            return [extract_docx(file_path, max_chars=max_chars)]
        if ext == ".svg":
            text_part, image = extract_svg(file_path, max_chars=max_chars)
            return [text_part, image] if image is not None else [text_part]
        if ext in IMAGE_EXTENSIONS:
            meta, image = extract_image(file_path)
            return [meta, image]
        return [
            f"오류: 지원하지 않는 확장자입니다 ({ext}). "
            f"지원 형식: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        ]
    except Exception as e:
        return [f"오류: '{file_path.name}' 처리 중 문제가 발생했습니다 - {type(e).__name__}: {e}"]


if __name__ == "__main__":
    mcp.run()
