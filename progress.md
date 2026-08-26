# progress.md

새 대화창에서도 "지금까지 어디까지 됐는지"를 이 파일만 읽고 복원할 수 있도록 기록한다.
갱신 시점을 함께 남긴다.

## 완료 (2026-08-26)

- `server.py` + `extractors/{pdf,pptx,docx,svg,image}.py` 구현.
  - `list_folder_structure(path, max_depth=5)` — 폴더 트리/확장자 집계 JSON.
  - `read_document(path, max_chars=20000, max_pages=30)` — 포맷별 텍스트/이미지 추출.
- `uv`로 프로젝트 스캐폴딩 (`uv init` + `uv add mcp pypdf python-pptx python-docx
  Pillow svglib reportlab`). 시스템 `python`이 PATH에 없어 `uv`가 인터프리터까지
  관리하도록 함.
- `mcp==2.1.1`(`FastMCP` → `MCPServer`로 개명된 버전)에 맞춰 API 확인 후 구현.
- `test_samples/`의 더미 5종(pdf/pptx/docx/svg/png)으로 각 추출기 직접 호출 검증
  완료 — 정상 동작 확인.
- Claude Code에 `claude mcp add file-analysis -s user -- uv run --directory
  <경로> python server.py`로 사용자 범위 등록 완료, `claude mcp list`에서
  `✔ Connected` 확인.
- Codex CLI에 `codex mcp add file-analysis -- uv run --directory <경로> python
  server.py`로 전역 등록 완료.
- 새 Claude Code 세션에서 실제 도구 호출로 end-to-end 검증 완료 — `test_samples/`
  폴더 구조 분석 + 사용자가 추가한 실제 문서(`proposal.pdf`, 삼성MX구미 Day2/Day3
  교육자료 PDF 2건) 전체 페이지 요약까지 정상 동작.
- 하네스 문서 4종(`AGENTS.md`/`plan.md`/`progress.md`/`decisions.md`) 작성 완료
  (이 작업 자체).

## 미착수

- 허용 폴더 allowlist.
- PDF 페이지 이미지 렌더링.
- 대용량 폴더 캐싱/증분 스캔.
- git 커밋 — 저장소는 `git init`은 되어 있으나 아직 커밋이 하나도 없는 상태
  (unborn master). 사용자가 명시적으로 요청하면 진행한다.

## 알려진 제약

- SVG 래스터화(`svglib`)는 일부 복잡한 SVG 기능(필터, 일부 그라디언트)을 완벽
  지원하지 않을 수 있음 — 실패 시 원문 XML 텍스트만 반환하도록 이미 처리됨.
- 경로가 매 호출 인자라 접근 범위 제한이 없음 — 신뢰 환경 개인용 전제.
