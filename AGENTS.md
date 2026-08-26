# AGENTS.md

이 프로젝트에서 작업을 시작하는 에이전트가 가장 먼저 읽어야 하는 지시문서입니다.
Day2 교육자료의 표현을 빌리면, 이 파일은 "에이전트를 위한 온보딩 매뉴얼"입니다.

## 프로젝트가 하는 일

`file-analysis-mcp`는 로컬 MCP 서버로, 지정한 폴더의 PDF/PPTX/DOCX/SVG/이미지를
읽어 **원문 텍스트와 이미지를 그대로** 반환합니다. **요약은 서버가 하지 않습니다** —
이 서버를 호출하는 호스트(Claude Code/Codex)가 반환된 내용을 읽고 직접 요약합니다.
이 원칙을 벗어나는 변경(예: 서버 안에서 LLM API를 호출해 요약문을 만드는 것)은
설계 취지에 어긋나므로 하지 않습니다.

## 폴더 구조 규칙

- `extractors/*.py`: 포맷별 순수 함수만 둔다. 각 함수는 `Path`를 받아 텍스트(str) 또는
  `(텍스트, Image)` 튜플을 반환한다. MCP 관련 타입(`mcp.server.mcpserver...`) 외에는
  이 레이어에서 MCP 프로토콜을 신경 쓰지 않는다.
- `server.py`: 얇은 디스패치 레이어만 담당한다 — 경로 검증 → 확장자별로 `extractors`
  함수 호출 → 결과를 도구 반환값으로 감싸기. 파싱 로직을 이 파일에 직접 넣지 않는다.
- `test_samples/`: 스모크 테스트용 샘플 파일. **사용자가 실제로 추가한 문서
  (`proposal.pdf`, `삼성MX구미_...pdf` 등)를 삭제·수정하지 않는다** — 필요하면
  더미 파일만 별도로 추가한다.

## 코딩 컨벤션

- 파일 처리 중 발생하는 예외는 서버를 죽이지 않는다 — `read_document`/
  `list_folder_structure` 안에서 잡아서 사람이 읽을 수 있는 한국어 에러 문자열로
  반환한다 (예: `extractors/__init__.py`의 `PathError` 패턴을 따른다).
- 텍스트 반환은 항상 `max_chars`(기본 20000)로 길이를 제한해 컨텍스트 폭주를 막는다.
  PDF는 추가로 `max_pages`(기본 30)로 페이지 수를 제한한다.
- 새 문서 포맷을 추가할 때도 이 두 제한 패턴을 그대로 따른다.

## 하지 말아야 할 것 (금지 행동)

- `test_samples/` 안의 실제 사용자 문서를 삭제·수정하지 않는다.
- `.venv/`, `__pycache__/`, `uv.lock`이 아닌 잠금파일 등 생성 산출물을 손으로 편집하지
  않는다 (필요하면 `uv add`/`uv sync`로만 관리).
- `mcp<2` 시절의 `from mcp.server.fastmcp import FastMCP` 스타일로 되돌리지 않는다.
  이 프로젝트는 `mcp==2.1.1`(`FastMCP`가 `MCPServer`로 개명된 버전)을 사용하며,
  올바른 import는 `from mcp.server.mcpserver import MCPServer`, 이미지 반환은
  `from mcp.server.mcpserver.utilities.types import Image`다. 이유는
  [decisions.md](decisions.md) 참고.
- 사용자에게 묻지 않고 `claude mcp add`/`codex mcp add`로 등록된 서버를 재등록하거나
  스코프를 바꾸지 않는다.

## 변경 후 검증 절차

1. `uv run python -c "import server"` — import 및 도구 등록이 깨지지 않았는지 확인.
2. `test_samples/`의 5개 더미 포맷(`sample.pdf/.pptx/.docx/.svg/.png`)에 대해
   `read_document`를 호출해 텍스트/이미지가 정상 반환되는지 스모크 테스트.
3. `list_folder_structure`로 `test_samples/`를 조회해 트리/확장자 집계가 정상인지 확인.

## 함께 읽을 문서

- [plan.md](plan.md) — 이 프로젝트의 목표와 아직 하지 않은 확장 항목.
- [progress.md](progress.md) — 현재까지 완료된 것과 미착수 항목.
- [decisions.md](decisions.md) — 왜 이런 선택을 했는지에 대한 근거.
