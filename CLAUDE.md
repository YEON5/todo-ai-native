# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# 언어규칙
- 모든 설명은 한글로 한다.

## Project
AI Native ToDo List. React, FastAPI, Supabase, Vercel로 만드는 ToDo List 웹앱입니다.

**현재 상태:** React와 FastAPI가 `/api/todos`로 연동되어 있습니다. 백엔드 저장소는 In-Memory라서 백엔드를 재시작하면 데이터가 사라집니다. Supabase 저장소와 배포는 아직입니다(docs/tasks.md Phase S, D).

## Development Rules
1. 기존 코드 구조를 먼저 확인한다.
2. 변경 전 구현 계획을 제시한다.
3. PRD와 API 명세를 준수한다. 명세는 `docs/`에 있고, 이 파일과 다르면 `docs/`가 우선한다.
   - `PRD.md`(FR/NFR), `api-spec.md`(API-xxx), `db-schema.md`(DB-xxx), `acceptance-criteria.md`(AC-xxx), `tasks.md`(TASK-xxx), `spec-review.md`(추적표, 미결 사항)
   - 작업과 보고는 요구사항 ID로 연결한다. 요구사항을 바꾸면 관련 문서를 함께 갱신한다.
4. UI는 이 파일의 "UI 디자인 규칙"을 따른다.
5. 기존 기능을 유지한다.
6. 구현 후 테스트 결과를 보고한다(아래 "테스트 정책" 형식).
7. 비밀 키를 코드에 포함하지 않는다.

## Tech Stack

| 영역 | 기술 | 상태 |
| --- | --- | --- |
| Frontend | React 19 + Vite + TypeScript, 순수 CSS (외부 UI 라이브러리 금지) | 구현됨 |
| Lint | oxlint (ESLint 아님, 설정: `frontend/.oxlintrc.json`) | 구현됨 |
| Backend | FastAPI + Pydantic v2, Python 3.12, pytest | 구현됨 (In-Memory 저장소) |
| Database / Auth | Supabase (PostgreSQL, Supabase Auth) | 예정 |
| Deployment | Vercel (프론트 정적 호스팅 + FastAPI 서버리스) | 예정 |

## Architecture

```text
frontend/      React UI (구현됨)
  src/App.tsx          할 일 상태와 추가/토글/수정/삭제 함수를 모두 소유
  src/components/      ProgressSummary, TodoInput, TodoItem
  src/api/todos.ts     /api/todos 호출 모듈. 컴포넌트는 fetch를 직접 쓰지 않는다
  src/types.ts         Todo 타입 { id, title, completed, created_at, due_date }, TITLE_MAX_LENGTH
  src/dates.ts         마감일(YYYY-MM-DD) 표시 변환. new Date('YYYY-MM-DD')를 쓰지 않는다(시간대 문제)
  src/index.css        디자인 토큰과 전체 스타일
backend/       FastAPI (구현됨)
  app/routers → services → repositories   호출 방향. 저장소 교체 지점은 app/dependencies.py
  tests/               pytest. conftest가 테스트마다 빈 In-Memory 저장소로 바꿔 끼운다
supabase/      DB 스키마·마이그레이션 (빈 폴더, 예정)
docs/          PRD, API 명세, DB 스키마, 수용 기준, TASKS, 명세 검토
lession/       강의 자료. 애플리케이션 코드가 아니므로 수정하지 않는다.
```

- **상태는 `App.tsx` 한 곳에만 둔다.** 컴포넌트는 콜백을 받아 호출하고, 자체 상태는 입력값·편집 모드 같은 UI 상태만 가진다. 백엔드 연동 시 App의 함수들만 API 호출로 바꾸면 되도록 이 구조를 유지한다.
- 환경 변수 목록은 [README.md](README.md)의 "환경 변수 (예정)" 표를 따른다.
- 브랜치: `main`(안정) / `develop`(통합) / `feature/*`(기능) / `supabase/*`(DB).

## 명령어

```bash
# frontend/ 에서 실행
npm install
npm run dev        # http://localhost:5173
npm run build      # tsc -b 타입 검사 + vite 빌드
npm run lint       # oxlint

# backend/ 에서 실행 (Python 3.12는 PATH에 없으므로 uv로 가상환경을 만든다)
uv venv .venv --python 3.12
uv pip install --python .venv -r requirements.txt
.venv/Scripts/python -m uvicorn app.main:app --reload --port 8000   # API 문서: http://localhost:8000/docs
.venv/Scripts/python -m pytest                                      # 전체 테스트
.venv/Scripts/python -m pytest tests/test_todos.py::test_ac_002_1_list_in_creation_order   # 테스트 하나만
```

## UI 디자인 규칙

**토큰**
- 색상과 폰트는 `src/index.css` 상단 `:root`의 CSS 변수만 쓴다. 하드코딩된 색을 넣지 않는다.
- 다크 모드는 `prefers-color-scheme: dark` 블록에서 같은 변수 이름으로 다시 정의한다. 새 토큰은 두 블록에 모두 추가한다.
- 색의 역할은 고정이다:

  | 토큰 | 용도 |
  | --- | --- |
  | `--moss` | 완료 표시, 진행 막대, 주 버튼 |
  | `--focus` (앰버) | 키보드 포커스 전용 |
  | `--rust` | 삭제. 평소에는 회색이고 호버·포커스 시에만 표시 |
  | `--paper` / `--surface` / `--line` | 배경 / 카드 / 테두리 |

- 폰트는 IBM Plex Sans KR 하나만 쓴다(`index.html`에서 Google Fonts로 로드). 숫자 표시는 `tabular-nums`를 쓴다.

**레이아웃**
- 최대 폭 560px의 왼쪽 정렬 단일 열이다. 순서는 날짜·제목 → 완료율 → 입력 카드 → 할 일 카드 목록.
- 할 일은 카드 하나에 하나씩 둔다. 카드는 그림자 없이 1px 테두리만 쓴다. 완료된 카드는 투명 배경과 점선 테두리로 뒤로 물러나게 한다.
- 완료율은 `ProgressSummary`가 할 일 하나당 막대 한 칸으로 그린다(목록 순서와 동일). 24개를 넘으면 연속 막대로 바뀐다.

**반응형**
- 모바일 기준점은 `max-width: 600px`이고 좌우 여백은 16px이다.
- 버튼 등 터치 대상은 40px 이상으로 한다.
- 수정·삭제 버튼은 호버할 때만 보이게 숨기지 않는다(터치·키보드 사용자를 위해).

**접근성과 포커스**
- 포커스 표시는 전역 `:focus-visible`(3px 앰버 외곽선) 하나로 통일한다. `outline: none`을 쓰지 않는다.
- 텍스트가 없는 아이콘 버튼은 `aria-label`에 할 일 내용을 넣는다(예: `'운동 30분' 삭제`).
- 입력창은 `<label>`을 연결한다(화면에서 숨길 때는 `.visually-hidden`).
- 포커스 이동 규칙:
  - 삭제 후에는 다음 할 일(없으면 이전 할 일)의 체크박스로, 목록이 비면 입력창으로 이동한다. `App.tsx`의 `focusAfterDelete`가 담당한다.
  - 편집을 저장하거나 취소하면 그 할 일의 수정 버튼으로 돌아온다. `TodoItem.tsx`가 담당한다.
  - 편집 중 Enter는 저장, Esc는 취소다.
- 체크박스 id `todo-check-${id}`와 입력창 id `new-todo`는 포커스 이동에 쓰이므로 바꾸지 않는다.
- `prefers-reduced-motion`이면 전환 효과를 끈다.

**문구**
- 화면 문구는 한국어로, 짧은 평서문으로 쓴다. `body`의 `word-break: keep-all`은 유지한다.
- 버튼 이름은 동작을 그대로 쓴다(추가, 저장, 취소).

## API 개발 규칙 (백엔드 구현 시)

**구조**
- `backend/app/` 아래를 다음처럼 나눈다:
  - `main.py`: 앱 생성, CORS, 라우터 등록
  - `routers/`: HTTP 처리만
  - `schemas/`: Pydantic 요청·응답 모델
  - `services/`: 비즈니스 로직
  - `repositories/`: 저장소. 먼저 In-Memory로 만들고, 나중에 같은 인터페이스의 Supabase 구현으로 교체한다
  - `core/`: 설정, Supabase 클라이언트
- 호출 방향은 Router → Service → Repository다. 라우터나 서비스에서 Supabase를 직접 호출하지 않는다.

**엔드포인트** (`/api/todos`. 자세한 요청·응답은 [docs/api-spec.md](docs/api-spec.md). 저장소를 바꿔도 경로와 응답 형식은 유지한다)

| 메서드 | 경로 | 동작 | 성공 코드 |
| --- | --- | --- | --- |
| GET | `/api/todos` | 목록 조회 (`created_at` 오름차순) | 200 |
| POST | `/api/todos` | 생성 | 201 |
| PATCH | `/api/todos/{id}` | 제목·완료 여부·마감일 수정 (`due_date: null`은 마감일 지우기) | 200 |
| DELETE | `/api/todos/{id}` | 삭제 | 204 |

**검증과 오류**
- 모든 입력은 Pydantic으로 검증한다. 할 일 내용은 앞뒤 공백을 제거한 뒤 비어 있으면 거부한다. 프론트와 같은 규칙이다.
- 잘못된 입력에는 422, 없는 id에는 404를 반환한다. 오류 메시지에는 무엇이 잘못됐는지 적는다.

**응답과 연동**
- 응답 필드는 `id`, `title`, `completed`, `created_at`, `due_date`(`YYYY-MM-DD` 또는 `null`)이다. 프론트 `Todo` 타입도 같은 이름을 쓰고, 이름을 변환하는 코드를 두지 않는다.
- 프론트에서 API를 부를 때는 `frontend/src/api/` 모듈을 통해서만 부르고, 주소는 `VITE_API_BASE_URL`로 받는다. CORS 허용 출처도 환경 변수로 설정한다.

**키와 DB 변경**
- `SUPABASE_SECRET_KEY`는 백엔드에서만 쓴다. 프론트는 Supabase에 직접 접근하지 않고 FastAPI만 호출한다(MVP, docs/spec-review.md R-14). `.env` 파일은 커밋하지 않는다.
- DB 스키마 변경은 `supabase/migrations/`에 SQL로 남기고, 기존 데이터를 보존하는 방식으로 작성한다.

## 테스트 정책

- **프론트엔드:** 테스트 프레임워크가 아직 없다. 모든 변경 후 `npm run build`와 `npm run lint`가 통과해야 한다. UI를 바꿨다면 실제 브라우저로 동작을 확인한다: 추가, 체크, 수정(Enter/Esc), 삭제, 빈 목록, 키보드 포커스 이동.
- **백엔드:** 기능마다 `backend/tests/`에 pytest 테스트를 작성한다. 테스트 이름은 수용 기준 ID로 시작한다(예: `test_ac_003_4_...`). 정상 경로와 오류 경로(422, 404)를 모두 다룬다. Supabase는 목(mock)이나 테스트 전용 프로젝트를 쓰고, 운영 DB와 실제 사용자 데이터는 건드리지 않는다.
- **회귀:** 새 기능을 넣을 때 기존 CRUD 동작이 그대로인지 함께 확인한다.
- **보고 형식:**
  - 실행한 명령과 결과를 적는다.
  - 확인한 항목마다 PASS / FAIL / SKIP을 표시하고, 실패하면 원인을 적는다.
  - 검증하지 못한 항목은 따로 밝힌다.
  - 테스트가 없거나 환경이 설정되지 않아 실행하지 못했다면 성공으로 보고하지 않는다.
