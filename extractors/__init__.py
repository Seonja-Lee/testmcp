from pathlib import Path


class PathError(Exception):
    """지정한 경로를 찾을 수 없거나 접근할 수 없을 때 발생."""


def resolve_path(path: str) -> Path:
    """사용자가 준 경로 문자열을 절대 경로로 정규화하고 존재 여부를 확인한다."""
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise PathError(f"경로를 찾을 수 없습니다: {p}")
    return p
