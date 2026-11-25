# DB 스키마

| 항목 | 내용 |
| --- | --- |
| 기준 문서 | [PRD.md](PRD.md), [api-spec.md](api-spec.md) |
| DB | Supabase PostgreSQL, `public` 스키마 |
| 마이그레이션 위치 | `supabase/migrations/` |

## DB-001 `todos` 테이블 — FR-001~005, FR-007

| 컬럼 | 타입 | 제약 | 기본값 | API 필드 |
| --- | --- | --- | --- | --- |
| `id` | `uuid` | PRIMARY KEY | `gen_random_uuid()` | `id` |
| `title` | `text` | NOT NULL, `CHECK (char_length(btrim(title)) BETWEEN 1 AND 200)` | 없음 | `title` |
| `completed` | `boolean` | NOT NULL | `false` | `completed` |
| `created_at` | `timestamptz` | NOT NULL | `now()` | `created_at` |

```sql
CREATE TABLE IF NOT EXISTS public.todos (
    id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    title      TEXT        NOT NULL
               CHECK (char_length(btrim(title)) BETWEEN 1 AND 200),
    completed  BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- API-001 목록은 created_at 오름차순으로 조회한다.
CREATE INDEX IF NOT EXISTS todos_created_at_idx ON public.todos (created_at);
```

- 제목 검증은 API(Pydantic)에서 먼저 하고, DB의 `CHECK`는 마지막 안전장치다. 두 규칙(공백 제거 후 1~200자)은 항상 같아야 한다.
- `IF NOT EXISTS`는 기존 테이블의 구조가 같다는 것을 보장하지 않는다. 실행 전후로 컬럼과 제약을 조회해서 확인한다.
- 기존 테이블을 삭제하거나 다시 만들지 않는다.

## DB-003 `todos.due_date` 컬럼 — FR-009

| 컬럼 | 타입 | 제약 | 기본값 | API 필드 |
| --- | --- | --- | --- | --- |
| `due_date` | `date` | NULL 허용 | `NULL` | `due_date` (`YYYY-MM-DD` 또는 `null`) |

DB-001을 만든 뒤 별도 마이그레이션으로 추가한다. 기존 행은 `NULL`(마감일 없음)이 되어 데이터가 보존된다.

```sql
-- supabase/migrations/0002_add_todos_due_date.sql (Supabase 단계에서 작성, 승인 후 실행)
ALTER TABLE public.todos ADD COLUMN IF NOT EXISTS due_date DATE;
```

- `timestamptz`가 아니라 `date`를 쓴다. 마감일은 시간과 시간대가 없는 달력 날짜라서, 서버와 브라우저의 시간대가 달라도 날짜가 하루 밀리지 않는다.
- 마감일 순 정렬은 범위 밖이라 인덱스를 만들지 않는다.
- **현재 In-Memory 단계에서는 이 SQL을 실행하지 않는다.** Supabase 저장소로 바꿀 때(TASK-S01) 함께 적용한다.

## DB-002 보안 (RLS) — NFR-004

```sql
ALTER TABLE public.todos ENABLE ROW LEVEL SECURITY;
```

- `anon`, `authenticated` 역할에는 정책을 만들지 않는다. 브라우저에서 Supabase로 직접 접근하는 것을 막기 위해서다.
- 데이터 접근은 FastAPI가 서버 전용 키(`SUPABASE_SECRET_KEY`)로만 한다. 이 키는 RLS를 우회하므로 백엔드 밖으로 내보내지 않는다.

## In-Memory 저장소와의 대응

Supabase로 바꾸기 전(TASK-B 단계)의 In-Memory 저장소도 같은 규칙을 따른다.
- `id`는 `uuid4()`, `created_at`은 UTC 현재 시각으로 만든다.
- 목록은 `created_at` 오름차순으로 반환한다.
- `due_date`는 Python `date` 또는 `None`으로 저장하고, 생략하면 `None`이다(DB-003의 `NULL`과 같음).

이렇게 해야 저장소를 바꿔도 API 응답이 달라지지 않는다(NFR-005).

## 변경하지 않는 것

`user_id`, `updated_at`, 카테고리 컬럼은 이번 범위에 없다(마감일은 DB-003으로 추가됨). 추가하게 되면 새 마이그레이션 파일로 추가하고, 기존 데이터에 기본값을 채운다.
