# file-analysis-mcp

지정한 폴더 안의 비정형 문서(PDF, PPTX, DOCX, SVG, PNG 등 이미지)를 읽어,
호출하는 호스트(Claude Code, Codex CLI 등)가 내용 요약과 폴더 구조 분석을
할 수 있도록 원문 텍스트/이미지를 그대로 전달하는 개인용 MCP 서버입니다.

이 서버는 요약을 직접 수행하지 않습니다 — 텍스트를 추출하고 이미지를
그대로 반환할 뿐이며, 실제 요약은 이 도구를 호출한 LLM(Claude Code/Codex)이
수행합니다. 별도 API 키가 필요 없습니다.

## 제공 도구

- `list_folder_structure(path, max_depth=5)`
  지정 폴더를 재귀 탐색해 트리 구조, 확장자별 파일 개수, 총 용량을 JSON으로 반환.
- `read_document(path, max_chars=20000, max_pages=30)`
  확장자에 따라 내용을 추출해 텍스트/이미지로 반환.
  - `.pdf` → 페이지별 텍스트
  - `.pptx` → 슬라이드별 텍스트 + 노트
  - `.docx` → 문단/제목/표 텍스트
  - `.svg` → 원문 XML + 래스터화된 PNG 이미지(가능한 경우)
  - `.png` / `.jpg` / `.jpeg` / `.bmp` / `.gif` / `.webp` → 이미지 그대로(리사이즈 후)

## 설치

`uv`가 파이썬 인터프리터와 의존성을 모두 관리합니다.

```bash
cd file-analysis-mcp
uv sync
```

## 로컬 테스트 (MCP Inspector)

```bash
npx @modelcontextprotocol/inspector uv run --directory . python server.py
```

브라우저에서 열리는 Inspector UI에서 `list_folder_structure`, `read_document`를
직접 호출해볼 수 있습니다. `test_samples/` 폴더에 PDF/PPTX/DOCX/SVG/PNG 샘플
파일이 준비되어 있어 바로 테스트 가능합니다.

## Claude Code에 등록

```bash
claude mcp add file-analysis -s user -- uv run --directory "C:\Users\20210\Desktop\testmcp\file-analysis-mcp" python server.py
```

이미 위 명령으로 사용자 범위(user scope)에 등록되어 모든 프로젝트에서 사용
가능합니다. **새 MCP 서버는 세션 시작 시 로드되므로, Claude Code를 재시작(또는
새 세션 시작)해야 도구가 나타납니다.** 등록 상태 확인: `claude mcp list`

## Codex CLI에 등록

```bash
codex mcp add file-analysis -- uv run --directory "C:\Users\20210\Desktop\testmcp\file-analysis-mcp" python server.py
```

이미 전역(global)으로 등록되어 있습니다. 확인: `codex mcp list`

## 사용 예시 (등록 후 새 세션에서)

> "C:\Users\me\Documents\보고서 폴더의 구조를 분석하고, 안에 있는 문서들을 요약해줘"

라고 요청하면 Claude Code/Codex가 `list_folder_structure`로 구조를 파악한 뒤
필요한 파일들에 `read_document`를 호출해 내용을 읽고 직접 요약합니다.

## 참고 / 제한사항

- 경로는 호출할 때마다 인자로 넘기는 방식이라 접근 폴더 제한(allowlist)은
  걸려있지 않습니다. 신뢰하는 로컬 환경에서 개인용으로 사용하는 것을 전제로
  합니다.
- 텍스트는 `max_chars`, PDF는 `max_pages`로 길이를 제한해 컨텍스트 폭주를
  방지합니다. 더 긴 내용이 필요하면 호출 시 값을 늘려서 요청하면 됩니다.
- SVG 래스터화(`svglib`)는 일부 복잡한 SVG 기능(필터, 그라디언트 일부 등)을
  완벽히 지원하지 않을 수 있습니다. 실패해도 원문 XML 텍스트는 항상 반환됩니다.
