# todo-ai-native

React, FastAPI, Supabase, Vercel로 만드는 ToDo List 웹 애플리케이션입니다.

> 현재 상태: React와 FastAPI가 연동된 CRUD가 동작합니다. 백엔드는 In-Memory 저장소를 써서 서버를 재시작하면 데이터가 사라집니다. Supabase 연동과 배포는 다음 단계입니다.

## 실행 방법

```bash
# 백엔드 (터미널 1)
cd backend
uv venv .venv --python 3.12
uv pip install --python .venv -r requirements.txt
.venv/Scripts/python -m uvicorn app.main:app --reload --port 8000

# 프론트엔드 (터미널 2)
cd frontend
npm install
npm run dev        # http://localhost:5173
```

API 문서(Swagger UI)는 http://localhost:8000/docs 에서 볼 수 있습니다. 명세는 [docs/](docs/)에 있습니다.

## 프로젝트 목적

- 할 일을 추가, 조회, 수정, 완료 처리, 삭제할 수 있는 ToDo List 서비스를 만듭니다.
- 프론트엔드(React)와 백엔드(FastAPI)를 나누고, 데이터 저장과 인증은 Supabase에 맡깁니다.
- 프론트엔드와 백엔드 모두 Vercel에 배포합니다.
- 작은 단위의 브랜치와 커밋으로 기능을 하나씩 추가합니다.

## 기술 스택

| 영역 | 기술 | 역할 |
| --- | --- | --- |
| Frontend | React (Vite, TypeScript) | 사용자 화면, API 호출 |
| Backend | FastAPI (Python) | REST API, 비즈니스 로직, 입력 검증 |
| Database / Auth | Supabase (PostgreSQL, Supabase Auth) | ToDo 데이터 저장, 사용자 인증 |
| Deployment | Vercel | 프론트엔드 정적 호스팅, FastAPI 서버리스 함수 |

## 초기 디렉터리 구조

```text
todo-ai-native/
├── frontend/              # React 앱 (Vite)
│   ├── public/
│   ├── src/
│   │   ├── components/    # 재사용 UI 컴포넌트
│   │   ├── pages/         # 화면 단위 컴포넌트
│   │   ├── api/           # 백엔드 API 호출 모듈
│   │   └── lib/           # 공통 유틸
│   └── package.json
├── backend/               # FastAPI 앱
│   ├── app/
│   │   ├── main.py        # FastAPI 진입점
│   │   ├── routers/       # API 라우터 (todos 등)
│   │   ├── schemas/       # Pydantic 요청/응답 모델
│   │   ├── services/      # 비즈니스 로직
│   │   ├── repositories/  # 저장소 (In-Memory → Supabase)
│   │   └── core/          # 설정, Supabase 연결
│   ├── tests/
│   └── requirements.txt
├── supabase/
│   └── migrations/        # DB 스키마 마이그레이션 SQL
├── docs/                  # PRD, API 명세, DB 스키마, 수용 기준, TASKS
├── lession/               # 강의 자료 (애플리케이션 코드 아님)
├── .gitignore
└── README.md
```

`frontend/`와 `backend/`는 구현되어 있고, `supabase/`는 아직 비어 있습니다. 실제 프론트 구조는 `src/components/`, `src/api/`이며, `pages/`와 `lib/`는 필요할 때 만듭니다.

## 브랜치 전략

현재 브랜치: `feature/todo-init` (아직 커밋 없음)

- `main`: 배포 가능한 안정 브랜치
- `develop`: 기능 브랜치를 모으는 통합 브랜치
- `feature/*`: 기능 개발 브랜치
- `supabase/*`: DB 관련 브랜치

## 환경 변수 (예정)

| 이름 | 사용처 | 설명 |
| --- | --- | --- |
| `VITE_API_BASE_URL` | frontend | FastAPI 서버 주소 |
| `VITE_SUPABASE_URL` | frontend | Supabase 프로젝트 URL (Supabase Auth를 도입할 때만, docs/spec-review.md R-06) |
| `VITE_SUPABASE_ANON_KEY` | frontend | Supabase 공개(anon) 키 (Supabase Auth를 도입할 때만) |
| `SUPABASE_URL` | backend | Supabase 프로젝트 URL |
| `SUPABASE_SECRET_KEY` | backend | Supabase 서버 전용 키 (서버에서만 사용, 커밋 금지) |
| `CORS_ORIGINS` | backend | API 호출을 허용할 프론트 주소 (쉼표로 구분) |
