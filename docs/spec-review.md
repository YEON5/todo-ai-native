# 명세 검토: 추적표, 누락, 충돌

구현 전에 PRD, API 명세, DB 스키마, 수용 기준, TASKS를 서로 대조하고, 기존 문서(README.md, CLAUDE.md), 현재 코드, 강의 교안 Module 7·8과도 비교한 결과입니다.

## 1. 요구사항 추적표

| 요구사항 | API | DB | 수용 기준 | TASK |
| --- | --- | --- | --- | --- |
| FR-001 생성 | API-002 | DB-001 | AC-001-1~5 | B02, B04, B05, B06, F03, F05 |
| FR-002 조회 | API-001 | DB-001 (인덱스) | AC-002-1~2 | B03, B05, F03 |
| FR-003 제목 수정 | API-003 | DB-001 | AC-003-1~5 | B02, B04, B05, F03, F06 |
| FR-004 완료 변경 | API-003 | DB-001 | AC-004-1~3 | B04, B05, F03 |
| FR-005 삭제 | API-004 | DB-001 | AC-005-1~3 | B04, B05, F03, F06 |
| FR-006 완료율 | (프론트 계산) | — | AC-006-1~2 | 구현됨 (회귀만 확인) |
| FR-007 영속성 | API-001~004 | DB-001 | AC-004-3, AC-007-1~3 | F03, S01, S03 |
| FR-008 로딩·오류 | API-000 오류 형식 | — | AC-008-1~3 | F02, F04 |
| FR-009 마감일 | API-000 마감일 검증, API-002, API-003 | DB-003 | AC-009-1~10 | 901~907 |
| NFR-001 접근성 | — | — | AC-N01, AC-003-2·3, AC-005-3 | F06 |
| NFR-002 반응형 | — | — | AC-N02 | (회귀만 확인) |
| NFR-003 디자인 | — | — | AC-N03 | (회귀만 확인) |
| NFR-004 보안 | API-000 (500 응답) | DB-002 | AC-N04 | 002, S02, D01, D02 |
| NFR-005 API 호환 | API-001~004 | DB-001 대응 | AC-007-3 | B03, S03 |
| NFR-006 테스트 | — | — | AC-N03 | B06, S04, D03 |

검토 결과, 모든 FR과 NFR에 수용 기준이 하나 이상 있습니다. 코드를 바꿔야 하는 FR에는 모두 TASK가 연결되어 있습니다. FR-006과 NFR-002·003은 이미 구현되어 있어서 회귀 확인만 합니다.

## 2. 발견한 충돌과 누락

| ID | 종류 | 내용 | 처리 | 상태 |
| --- | --- | --- | --- | --- |
| R-01 | 충돌 | API 경로: CLAUDE.md는 `/todos`, 교안 Module 7·8은 `/api/todos` | `/api/todos`로 통일. Vercel 서버리스 함수 경로(`/api`)와도 맞음. CLAUDE.md 수정함 | 해결 |
| R-02 | 충돌 | 필드 이름: 프론트 `Todo.text` ↔ 교안 DB `title`(FR-003 "제목 수정") | API와 DB는 `title`로 하고, 프론트 타입도 `title`로 바꿈(TASK-F01). 이름을 변환하는 코드를 따로 두지 않기 위해서임 | 해결 |
| R-03 | 충돌 | 서버 키 환경 변수: README·CLAUDE.md는 `SUPABASE_SERVICE_ROLE_KEY`, 교안은 `SUPABASE_SECRET_KEY` | 교안 방침(한 이름으로 통일)에 따라 `SUPABASE_SECRET_KEY`로 통일. README·CLAUDE.md 수정함 | 해결 |
| R-04 | 누락 | 제목 최대 길이가 어디에도 없음. 지금 프론트에는 제한이 없음 | 공백 제거 후 1~200자로 제안(API·DB·프론트 동일) | **결정 필요** |
| R-05 | 충돌 | 백엔드 계층: CLAUDE.md는 Router–Service(서비스가 Supabase 호출), 교안은 Router–Service–Repository(In-Memory → Supabase 교체) | Repository 계층 추가. CLAUDE.md 수정함 | 해결 |
| R-06 | 충돌 | README는 "Supabase Auth, 사용자 인증"을 기술 스택에 넣었지만, 이번 범위에는 인증이 없음. 교안은 인증 없는 MVP는 공개 배포하지 말라고 함 | MVP는 인증 없는 단일 공유 목록으로 하고 PRD Out of Scope에 명시함. 공개 배포 전에 다시 결정(TASK-D02) | **결정 필요** |
| R-07 | 누락 | 목록 순서가 정의되지 않음 | `created_at` 오름차순(지금 화면처럼 새 할 일이 아래로) | 해결 |
| R-08 | 누락 | 서버 실패와 로딩 상태 요구사항이 없음. 지금 앱은 실패할 일이 없어서 고려하지 않았음 | FR-008 추가. 응답 성공 후 화면 반영(비관적 갱신) | 해결 |
| R-09 | 충돌 | 지금 프론트는 `crypto.randomUUID()`로 id를 만들지만, 명세는 서버가 id를 만듦 | 서버 응답의 id를 사용(TASK-F03). 프론트에서 id 생성 코드는 제거 | 해결 |
| R-10 | 누락 | PATCH 본문이 비어 있을 때의 동작이 없음 | 422 반환(API-003) | 해결 |
| R-11 | 충돌 | 교안 안에서 문서 이름이 다름: Module 6은 `acceptance-criteria.md`, Module 8은 `acceptance.md`. Module 6 산출물에는 `requirements.md`도 있음 | `acceptance-criteria.md` 사용. 교안 설명("여기서는 CLAUDE.md")에 따라 기능·비기능 요구사항은 별도 `requirements.md` 없이 PRD 4·5장에 둠 | 해결 |
| R-12 | 충돌 | CLAUDE.md는 검증 오류를 "422(또는 400)"이라고 함. 명세는 422 하나 | 422로 통일. CLAUDE.md 수정함 | 해결 |
| R-13 | 확인 | 삭제는 확인 창도, 되돌리기도 없음. 실수로 지우면 복구할 수 없음 | 지금 동작을 유지(PRD FR-005에 명시). 필요하면 이후 기능으로 추가 | 유지 |
| R-14 | 충돌 | README는 프론트 환경 변수로 `VITE_SUPABASE_URL`·`VITE_SUPABASE_ANON_KEY`와 `src/lib`의 "Supabase 클라이언트"를 계획했지만, DB-002는 브라우저의 Supabase 직접 접근을 막음 | MVP에서 프론트는 FastAPI만 호출. anon 키 두 개는 R-06에서 Supabase Auth를 고를 때만 쓰는 것으로 README에 표시. CLAUDE.md 수정함 | 해결 |
| R-15 | 충돌 | 기존 API-003은 PATCH에서 모든 필드의 `null`을 거부함. 그런데 마감일을 지우려면 `due_date: null`이 필요함 | `due_date`만 `null` 허용(지우기 의미). `title`·`completed`의 `null`은 계속 422. 기존 테스트(AC-003-4)도 그대로 통과해야 함 | 해결 |
| R-16 | 누락 | 마감일의 시간·시간대 처리가 정의되지 않음. JS `new Date('YYYY-MM-DD')`는 UTC로 해석되어 하루가 밀릴 수 있음 | 날짜만 저장(DB `date`, API `YYYY-MM-DD`). 프론트는 연·월·일로 나눠 로컬 날짜로 표시 | 해결 |
| R-17 | 확인 | Pydantic 기본(lax) 모드는 숫자(유닉스 시간)나 `2026-11-28T00:00:00`도 날짜로 받아들임. 명세의 "정확히 YYYY-MM-DD"와 어긋남 | 스키마에서 정규식으로 문자열 형식을 먼저 검사한 뒤 날짜로 변환(AC-009-6) | 해결 |

## 3. 결정이 필요한 항목

1. **R-04 제목 최대 길이**: 200자로 해도 될까요? 다른 값을 정하면 api-spec, db-schema, acceptance-criteria(AC-001-4), TASK-F05를 함께 바꿉니다.
2. **R-06 인증**: MVP를 인증 없는 공유 목록으로 진행해도 될까요? 그렇다면 공개 배포 전(TASK-D02)에 다음 중 하나를 정해야 합니다.
   - 배포 URL을 비공개로 유지
   - 간단한 인증 추가
   - Supabase Auth와 `user_id` 컬럼 도입. 이 경우 DB·API·PRD 범위가 바뀝니다.
