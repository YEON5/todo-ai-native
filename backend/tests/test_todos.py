"""/api/todos CRUD 테스트. 각 테스트 이름 앞의 ID는 docs/acceptance-criteria.md의 수용 기준이다."""

from datetime import datetime
from uuid import UUID, uuid4

import pytest

URL = "/api/todos"
MISSING_ID = "00000000-0000-4000-8000-000000000000"


# ---------- FR-001 생성 (API-002) ----------


def test_ac_001_1_create_returns_201_with_defaults(client):
    response = client.post(URL, json={"title": "운동 30분"})

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"id", "title", "completed", "created_at", "due_date"}
    assert body["title"] == "운동 30분"
    assert body["completed"] is False
    UUID(body["id"])
    assert datetime.fromisoformat(body["created_at"]).tzinfo is not None


def test_ac_001_2_create_strips_whitespace(create):
    assert create("  운동  ")["title"] == "운동"


@pytest.mark.parametrize("title", ["", "   ", "\t\n"])
def test_ac_001_3_create_rejects_blank_title(client, title):
    assert client.post(URL, json={"title": title}).status_code == 422


def test_ac_001_3_create_rejects_missing_or_non_string_title(client):
    assert client.post(URL, json={}).status_code == 422
    assert client.post(URL, json={"title": None}).status_code == 422
    assert client.post(URL, json={"title": 123}).status_code == 422


def test_ac_001_4_create_title_length_limit(client):
    assert client.post(URL, json={"title": "가" * 200}).status_code == 201
    assert client.post(URL, json={"title": "가" * 201}).status_code == 422
    # 길이는 공백을 제거한 뒤에 센다.
    assert client.post(URL, json={"title": f"  {'가' * 200}  "}).status_code == 201


def test_create_ignores_client_supplied_fields(client):
    client_id = str(uuid4())
    response = client.post(
        URL, json={"title": "A", "id": client_id, "completed": True, "created_at": "2000-01-01T00:00:00Z"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] != client_id
    assert body["completed"] is False
    assert not body["created_at"].startswith("2000")


# ---------- FR-002 조회 (API-001) ----------


def test_ac_002_1_list_in_creation_order(client, create):
    ids = [create(t)["id"] for t in ["A", "B", "C"]]

    response = client.get(URL)

    assert response.status_code == 200
    assert [t["id"] for t in response.json()] == ids


def test_ac_002_2_list_empty(client):
    response = client.get(URL)

    assert response.status_code == 200
    assert response.json() == []


# ---------- FR-003 제목 수정 (API-003) ----------


def test_ac_003_1_update_title_keeps_completed(client, create):
    todo = create("A")
    client.patch(f"{URL}/{todo['id']}", json={"completed": True})

    response = client.patch(f"{URL}/{todo['id']}", json={"title": "  A2 "})

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "A2"
    assert body["completed"] is True
    assert body["id"] == todo["id"]
    assert body["created_at"] == todo["created_at"]


def test_update_title_and_completed_together(client, create):
    todo = create("A")

    body = client.patch(f"{URL}/{todo['id']}", json={"title": "B", "completed": True}).json()

    assert (body["title"], body["completed"]) == ("B", True)


@pytest.mark.parametrize(
    "payload",
    [
        {},  # 빈 본문
        {"title": "   "},  # 공백 제목
        {"title": "가" * 201},  # 너무 긴 제목
        {"title": None},  # null
        {"completed": None},
        {"completed": "true"},  # boolean이 아님
        {"completed": 1},
    ],
)
def test_ac_003_4_update_rejects_invalid_body(client, create, payload):
    todo = create("A")

    assert client.patch(f"{URL}/{todo['id']}", json=payload).status_code == 422
    # 실패한 요청은 데이터를 바꾸지 않는다.
    assert client.get(URL).json()[0]["title"] == "A"


def test_ac_003_5_update_missing_id_returns_404(client):
    response = client.patch(f"{URL}/{MISSING_ID}", json={"title": "A"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}


def test_update_invalid_uuid_returns_422(client):
    assert client.patch(f"{URL}/not-a-uuid", json={"title": "A"}).status_code == 422


# ---------- FR-004 완료 상태 변경 (API-003) ----------


def test_ac_004_1_toggle_completed_keeps_title(client, create):
    todo = create("A")

    done = client.patch(f"{URL}/{todo['id']}", json={"completed": True}).json()
    undone = client.patch(f"{URL}/{todo['id']}", json={"completed": False}).json()

    assert (done["completed"], done["title"]) == (True, "A")
    assert undone["completed"] is False
    assert client.get(URL).json()[0]["completed"] is False


# ---------- FR-005 삭제 (API-004) ----------


def test_ac_005_1_delete_removes_only_target(client, create):
    a, b, c = (create(t) for t in ["A", "B", "C"])

    response = client.delete(f"{URL}/{b['id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert [t["id"] for t in client.get(URL).json()] == [a["id"], c["id"]]


def test_ac_005_2_delete_missing_or_already_deleted_returns_404(client, create):
    todo = create("A")
    assert client.delete(f"{URL}/{todo['id']}").status_code == 204

    assert client.delete(f"{URL}/{todo['id']}").status_code == 404
    assert client.delete(f"{URL}/{MISSING_ID}").status_code == 404


def test_delete_invalid_uuid_returns_422(client):
    assert client.delete(f"{URL}/not-a-uuid").status_code == 422


# ---------- FR-009 마감일 (API-002, API-003) ----------

INVALID_DUE_DATES = [
    "2026-02-30",  # 없는 날짜
    "2026-13-01",
    "2026/11/28",  # 다른 구분자
    "2026-11-28T00:00:00",  # 시간 포함
    "26-11-28",
    "",
    20261128,  # 숫자
    1764288000,  # 유닉스 시간
    True,
]


def test_ac_009_1_create_without_due_date(client):
    body = client.post(URL, json={"title": "A"}).json()

    assert body["due_date"] is None
    assert client.post(URL, json={"title": "B", "due_date": None}).json()["due_date"] is None


def test_ac_009_2_create_with_due_date(client):
    response = client.post(URL, json={"title": "A", "due_date": "2026-11-28"})

    assert response.status_code == 201
    assert response.json()["due_date"] == "2026-11-28"
    assert client.get(URL).json()[0]["due_date"] == "2026-11-28"


def test_ac_009_3_update_due_date_keeps_other_fields(client):
    todo = client.post(URL, json={"title": "A", "due_date": "2026-11-28"}).json()
    client.patch(f"{URL}/{todo['id']}", json={"completed": True})

    response = client.patch(f"{URL}/{todo['id']}", json={"due_date": "2026-11-30"})

    assert response.status_code == 200
    body = response.json()
    assert (body["due_date"], body["title"], body["completed"]) == ("2026-11-30", "A", True)


def test_ac_009_3_set_due_date_on_todo_without_one(client, create):
    todo = create("A")

    body = client.patch(f"{URL}/{todo['id']}", json={"due_date": "2026-12-01"}).json()

    assert body["due_date"] == "2026-12-01"


def test_ac_009_4_clear_due_date_with_null(client):
    todo = client.post(URL, json={"title": "A", "due_date": "2026-11-28"}).json()

    response = client.patch(f"{URL}/{todo['id']}", json={"due_date": None})

    assert response.status_code == 200
    assert response.json()["due_date"] is None
    assert client.get(URL).json()[0]["due_date"] is None


@pytest.mark.parametrize("payload", [{"title": "A2"}, {"completed": True}])
def test_ac_009_5_other_updates_keep_due_date(client, payload):
    todo = client.post(URL, json={"title": "A", "due_date": "2026-11-28"}).json()

    body = client.patch(f"{URL}/{todo['id']}", json=payload).json()

    assert body["due_date"] == "2026-11-28"


@pytest.mark.parametrize("due_date", INVALID_DUE_DATES)
def test_ac_009_6_create_rejects_invalid_due_date(client, due_date):
    response = client.post(URL, json={"title": "A", "due_date": due_date})

    assert response.status_code == 422
    assert client.get(URL).json() == []


@pytest.mark.parametrize("due_date", INVALID_DUE_DATES)
def test_ac_009_6_update_rejects_invalid_due_date(client, due_date):
    todo = client.post(URL, json={"title": "A", "due_date": "2026-11-28"}).json()

    response = client.patch(f"{URL}/{todo['id']}", json={"due_date": due_date})

    assert response.status_code == 422
    assert client.get(URL).json()[0]["due_date"] == "2026-11-28"


def test_ac_009_7_past_due_date_is_allowed(client):
    response = client.post(URL, json={"title": "A", "due_date": "2020-01-01"})

    assert response.status_code == 201
    assert response.json()["due_date"] == "2020-01-01"


# ---------- API-000 공통 ----------


def test_cors_allows_dev_frontend(client):
    response = client.options(
        URL,
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "PATCH"},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_unexpected_error_returns_generic_500(client):
    # client 픽스처가 끝날 때 dependency_overrides를 정리한다.
    from fastapi.testclient import TestClient

    from app.dependencies import get_todo_repository
    from app.main import app

    class BrokenRepository:
        def list(self):
            raise RuntimeError("db password=secret")

    app.dependency_overrides[get_todo_repository] = lambda: BrokenRepository()
    with TestClient(app, raise_server_exceptions=False) as broken_client:
        response = broken_client.get(URL)

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert "secret" not in response.text
