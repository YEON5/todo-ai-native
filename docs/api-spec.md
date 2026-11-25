# API 명세

| 항목 | 내용 |
| --- | --- |
| 기준 문서 | [PRD.md](PRD.md) |
| Base URL | 개발: `http://localhost:8000` / 프론트는 `VITE_API_BASE_URL`로 받음 |
| 형식 | JSON (`Content-Type: application/json`), 문자 인코딩 UTF-8 |
| 인증 | 없음 (MVP, [spec-review.md](spec-review.md) R-06) |

## 공통 규칙 (API-000)

**Todo 객체**

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `id` | string (UUID) | 서버가 생성 |
| `title` | string | 1~200자, 앞뒤 공백 제거됨 |
| `completed` | boolean | 기본값 `false` |
| `created_at` | string (ISO 8601, UTC) | 서버가 생성. 예: `2026-11-25T09:30:00Z` |
| `due_date` | string (`YYYY-MM-DD`) 또는 `null` | 마감일 (FR-009). 날짜만 있고 시간·시간대는 없다. 기본값 `null` |

```json
{
  "id": "3f1c2a9e-6b1d-4c1e-9a55-0d6f3c2b7e11",
  "title": "주간 회의 자료 정리",
  "completed": false,
  "created_at": "2026-11-25T09:30:00Z",
  "due_date": "2026-11-28"
}
```

**제목 검증**: 앞뒤 공백을 제거한 뒤 길이가 0이거나 200을 넘으면 422를 반환한다.

**마감일 검증** (FR-009): `null` 또는 정확히 `YYYY-MM-DD` 형식의 실제 날짜 문자열만 받는다. 지난 날짜도 허용한다. 다음은 422다.
- 없는 날짜: `2026-02-30`
- 다른 형식: `2026/11/28`, `2026-11-28T00:00:00`
- 문자열이 아닌 값: 숫자, boolean

**오류 응답 형식** (FastAPI 기본 형식을 따름)

| 코드 | 언제 | 본문 예 |
| --- | --- | --- |
| 404 | 없는 `id` | `{ "detail": "Todo not found" }` |
| 422 | 검증 실패, 잘못된 UUID, 빈 PATCH 본문 | `{ "detail": [ { "loc": ["body", "title"], "msg": "...", "type": "..." } ] }` |
| 500 | 저장소(DB) 오류 | `{ "detail": "Internal server error" }`. 내부 오류 내용은 응답에 넣지 않는다 |

**CORS**: 허용 출처는 환경 변수 `CORS_ORIGINS`(쉼표 구분)로 설정한다. 개발 기본값은 `http://localhost:5173`.

---

## API-001 목록 조회 — FR-002, FR-007

`GET /api/todos`

- 응답 `200`: `Todo[]`, `created_at` 오름차순(오래된 것이 먼저). 화면 순서와 같다.
- 할 일이 없으면 `[]`.

## API-002 생성 — FR-001, FR-007, FR-009

`POST /api/todos`

요청:
```json
{ "title": "운동 30분" }
{ "title": "보고서 제출", "due_date": "2026-11-28" }
```

- `title` 필수, `due_date` 선택(생략하거나 `null`이면 마감일 없음).
- 그 밖의 필드(`id`, `completed`, `created_at`)는 보내도 무시한다.
- 응답 `201`: 생성된 `Todo` (`completed: false`).
- 오류: `422` 제목 또는 마감일 검증 실패.

## API-003 수정 — FR-003, FR-004, FR-007, FR-009

`PATCH /api/todos/{id}`

요청 (`title`, `completed`, `due_date` 중 하나 이상 필수):
```json
{ "title": "운동 40분" }
{ "completed": true }
{ "due_date": "2026-11-30" }
{ "due_date": null }
{ "title": "운동 40분", "completed": true, "due_date": "2026-11-30" }
```

- 보낸 필드만 바꾼다.
- `due_date: null`은 마감일을 지운다. 반면 `title`과 `completed`에는 `null`을 보낼 수 없다(422).
- 응답 `200`: 수정된 `Todo` 전체.
- 오류:
  - `404`: 없는 id
  - `422`: 제목·마감일 검증 실패, `completed`가 boolean이 아님, 본문이 비어 있음(`{}`), id가 UUID 형식이 아님

## API-004 삭제 — FR-005, FR-007

`DELETE /api/todos/{id}`

- 응답 `204`: 본문 없음.
- 오류: `404` 없는 id(이미 삭제됨 포함), `422` id가 UUID 형식이 아님.

---

## 프론트엔드 연동 규칙 — FR-008

- 모든 호출은 `frontend/src/api/todos.ts`를 거친다. 컴포넌트에서 `fetch`를 직접 쓰지 않는다.
- 응답 필드 `title`, `completed`, `created_at`, `due_date`는 그대로 프론트 `Todo` 타입으로 쓴다(필드 이름 변환 없음). → R-02
- `due_date`는 날짜 문자열 그대로 다룬다. 화면 표시용으로 바꿀 때는 `new Date('2026-11-28')`처럼 문자열을 바로 넘기지 않는다. 이렇게 하면 UTC 자정으로 해석되어 시간대에 따라 하루가 밀린다. 연·월·일로 나눠 로컬 날짜로 만든다. → R-16
- 요청이 실패하면(네트워크 오류 또는 4xx/5xx) 화면 상태를 바꾸지 않고 오류 메시지를 보여준다.
