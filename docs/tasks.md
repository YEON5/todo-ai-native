# 구현 TASKS

순서대로 진행합니다. 각 작업은 관련 요구사항(FR/NFR)과 완료 확인 기준(AC)에 연결됩니다.

## Phase 0. 명세 확정 (구현 전)

| ID | 작업 | 관련 | 완료 기준 |
| --- | --- | --- | --- |
| TASK-001 | [spec-review.md](spec-review.md)의 "결정 필요" 항목(R-06 인증, R-04 제목 길이)을 확정하고 문서에 반영 | 전체 | 검토 문서의 미결 항목 0개 |
| TASK-002 | 루트 `.gitignore` 작성: `.env`, `.env.*`, `!.env.example`, `node_modules`, `dist`, `__pycache__`, `.venv` | NFR-004 | `git status`에 비밀·빌드 파일이 보이지 않음 |

## Phase B. 백엔드 (In-Memory) — 교안 Module 7

| ID | 작업 | 관련 | 완료 기준 |
| --- | --- | --- | --- |
| TASK-B01 | `backend/` 골격: `app/main.py`, `requirements.txt`(fastapi, uvicorn, pydantic, pytest, httpx), CORS 설정(`CORS_ORIGINS`) | API-000 | `uvicorn app.main:app --reload` 실행 후 `/docs` 접속 |
| TASK-B02 | `schemas/todo.py`: `TodoCreate`, `TodoUpdate`(최소 1개 필드), `Todo` 응답 모델, 제목 공백 제거와 1~200자 검증 | API-000 | AC-001-2~4, AC-003-4 |
| TASK-B03 | `repositories/`: `TodoRepository` 인터페이스와 `InMemoryTodoRepository`(created_at 오름차순) | DB-001, NFR-005 | 단위 테스트 통과 |
| TASK-B04 | `services/todo_service.py`: 생성·조회·수정·삭제, 없는 id면 NotFound | FR-001~005 | — |
| TASK-B05 | `routers/todos.py`: API-001~004 (`/api/todos`), 상태 코드 201/200/204/404/422 | API-001~004 | — |
| TASK-B06 | `tests/test_todos.py`: AC-001~005의 API 항목 전부 | NFR-006 | `pytest` 전부 PASS |

## Phase F. 프론트엔드 연동 — 교안 Module 7

| ID | 작업 | 관련 | 완료 기준 |
| --- | --- | --- | --- |
| TASK-F01 | `Todo` 타입을 `{ id, title, completed, created_at }`로 변경하고 `text` 사용처를 모두 `title`로 변경 | R-02 | 빌드 통과, 기존 UI 동작 동일 |
| TASK-F02 | `src/api/todos.ts`: `VITE_API_BASE_URL` 기반 `list/create/update/remove`, 실패 시 오류 throw | API-001~004 | — |
| TASK-F03 | `App.tsx`: 시작 시 목록 조회, 각 동작을 API 호출로 교체(응답 성공 후 상태 반영) | FR-001~005, FR-007 | AC-001-1, AC-002-2, AC-004-3, AC-007-1 |
| TASK-F04 | 로딩·오류 표시와 다시 시도 버튼. 추가 실패 시 입력값 유지. 처리 중 중복 클릭 방지 | FR-008 | AC-008-1~3 |
| TASK-F05 | 입력창·편집창에 `maxLength={200}` 적용 | R-04 | AC-001-4와 같은 규칙 |
| TASK-F06 | 포커스 이동 회귀 확인(삭제 후 포커스 이동이 서버 응답 이후에도 동작하는지) | NFR-001 | AC-003-2·3, AC-005-3, AC-N01 |
| TASK-F07 | `frontend/.env.example`에 `VITE_API_BASE_URL=http://localhost:8000` | — | — |

## Phase 9. 마감일 (FR-009) — 교안 3교시 `/todo-feature`

| ID | 작업 | 관련 | 완료 기준 |
| --- | --- | --- | --- |
| TASK-901 | 명세 갱신: PRD FR-009, API-002·003, DB-003, AC-009-x, 추적표 | FR-009 | 문서 간 ID 연결 |
| TASK-902 | `schemas/todo.py`: `due_date` 형식 검증(`YYYY-MM-DD` 문자열만), PATCH에서 `due_date: null` 허용 | API-002·003 | AC-009-4·6 |
| TASK-903 | Repository(인터페이스·In-Memory)와 Service의 `create`에 `due_date` 전달 | DB-003, NFR-005 | AC-009-1·2·7 |
| TASK-904 | pytest: AC-009-1~7, 기존 응답 필드 검사 갱신 | NFR-006 | 전체 PASS |
| TASK-905 | 프론트 타입·API 모듈에 `due_date`, 입력 카드에 날짜 입력, 카드에 마감일 표시와 편집 | FR-009 | AC-009-8~10 |
| TASK-906 | 기존 CRUD·포커스·모바일 회귀 확인 | NFR-001·002 | AC-001~008, AC-N01~N03 |
| TASK-907 | (Supabase 단계) `0002_add_todos_due_date.sql` 작성·승인 후 실행 | DB-003 | TASK-S01과 함께 |

## Phase S. Supabase 저장소 — 교안 Module 8

| ID | 작업 | 관련 | 완료 기준 |
| --- | --- | --- | --- |
| TASK-S01 | `supabase/migrations/0001_create_todos.sql`: DB-001, DB-002 | DB-001, DB-002 | 실행 전후 스키마 조회 결과가 문서와 일치 |
| TASK-S02 | `backend/.env.example`: `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, `CORS_ORIGINS` | NFR-004 | 실제 값은 커밋되지 않음 |
| TASK-S03 | `SupabaseTodoRepository` 구현(UUID·날짜 직렬화), 설정값에 따라 저장소 선택. Router와 Service는 변경 없음 | FR-007, NFR-005 | AC-007-2, AC-007-3 |
| TASK-S04 | 테스트는 In-Memory 저장소 또는 테스트 전용 데이터로만 실행(운영 데이터 변경 금지) | NFR-006 | `pytest` 전부 PASS |

## Phase D. 배포 — 교안 Module 8

| ID | 작업 | 관련 | 완료 기준 |
| --- | --- | --- | --- |
| TASK-D01 | Vercel 프론트·백엔드 프로젝트 설정, 환경 변수 등록 | NFR-004 | 배포 URL에서 AC-007-1 PASS |
| TASK-D02 | 공개 배포 전 R-06(인증 없는 공개 노출) 위험 처리 확인 | NFR-004 | 결정 기록 |
| TASK-D03 | 전체 수용 기준 회귀 실행 후 PASS/FAIL/SKIP 표 작성 | 전체 | 모든 AC PASS |
