# decisions.md

왜 이렇게 만들었는지 근거를 남긴다. 나중에 되돌아볼 때 "그때 왜 이렇게 했지?"에
답하기 위한 기록이다.

## Python + uv를 선택

이 머신은 시스템 `python`이 PATH에 없고(Windows Store 앱 실행 별칭만 존재)
`uv`는 설치되어 있었다. `uv`가 인터프리터·가상환경·의존성을 모두 관리하므로
이 문제를 우회할 수 있었다. Node도 있었지만, 문서 파싱 생태계(pypdf,
python-pptx, python-docx, Pillow)가 Python 쪽이 훨씬 풍부해 Python을 택했다.

## `mcp==2.1.1`의 `MCPServer` API 사용 (구 `FastMCP`)

`uv add mcp`로 설치했더니 최신 버전이 설치되었고, 실행해보니
`from mcp.server.fastmcp import FastMCP`가 `ModuleNotFoundError`를 내며
`mcp 2.x에서 FastMCP가 MCPServer로 이름이 바뀌었다`는 안내를 직접 출력했다.
온라인의 예제 코드 대부분은 아직 구버전(`FastMCP`, `mcp<2`) 기준이므로, 이
프로젝트를 참고해서 코드를 고칠 때 이 차이를 반드시 인지해야 한다.
올바른 import: `from mcp.server.mcpserver import MCPServer`,
`from mcp.server.mcpserver.utilities.types import Image`.

## 요약은 서버가 아니라 호출자(Host)가 수행

두 가지 옵션이 있었다: (a) 서버가 추출만 하고 호출자가 요약, (b) 서버 내부에서
Anthropic API를 호출해 직접 요약문을 생성. 사용자가 (a)를 선택했다 — API 키
관리가 필요 없고 구조가 단순하며, 호출하는 호스트 모델의 성능을 그대로 활용할
수 있기 때문이다. 이 때문에 `read_document`는 절대 요약문을 반환하지 않고
원문 텍스트/이미지만 반환하도록 설계했다.

## 폴더는 고정 설정이 아니라 매 호출 인자로 전달

서버 실행 시 환경변수 등으로 대상 폴더를 고정하는 방식도 고려했지만, 사용자가
유연성을 우선시해 매 도구 호출마다 `path` 인자로 넘기는 방식을 택했다.
대신 접근 범위 제한(allowlist)이 없다는 트레이드오프가 있음을 `plan.md`의
"향후 확장"에 남겨두었다.

## 이미지는 OCR 대신 그대로 반환해 호스트가 직접 봄

PNG/SVG의 "내용"을 이해하려면 비전 능력이 필요한데, 사용자가 OCR 대신 "이미지를
그대로 반환해 Claude가 직접 본다"를 선택했다. Claude Code/Codex 같은 호스트가
멀티모달이라는 전제 하에, 별도 OCR 의존성(Tesseract 등 외부 설치 필요) 없이도
동작하기 때문이다.

## SVG 래스터화에 `cairosvg` 대신 `svglib` + `reportlab`

`cairosvg`는 Cairo/GTK 네이티브 라이브러리가 필요해 Windows에서 설치가 까다롭다.
`svglib`+`reportlab`은 둘 다 순수 파이썬 wheel이라 `uv add`만으로 설치되고,
Windows에서 추가 네이티브 의존성 설치 없이 동작한다. 대신 일부 복잡한 SVG 기능
지원이 `cairosvg`보다 제한적일 수 있다는 트레이드오프가 있다 — 래스터화 실패 시
예외를 잡아 원문 XML 텍스트만 반환하도록 처리해 이 리스크를 흡수했다.
