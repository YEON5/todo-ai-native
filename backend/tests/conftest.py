import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_todo_repository
from app.main import app
from app.repositories.todo_repository import InMemoryTodoRepository


@pytest.fixture
def client():
    """테스트마다 빈 In-Memory 저장소를 쓴다. 테스트끼리 데이터가 섞이지 않는다."""
    repository = InMemoryTodoRepository()
    app.dependency_overrides[get_todo_repository] = lambda: repository
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def create(client):
    """제목으로 Todo를 만들고 응답 JSON을 반환한다."""

    def _create(title: str) -> dict:
        response = client.post("/api/todos", json={"title": title})
        assert response.status_code == 201, response.text
        return response.json()

    return _create
