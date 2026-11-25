"""Todo 저장소 (docs/db-schema.md DB-001, NFR-005).

Service는 TodoRepository 인터페이스에만 의존한다. 지금은 In-Memory 구현을 쓰고,
Supabase 단계(TASK-S03)에서 같은 인터페이스의 구현을 추가해 교체한다.
"""

from datetime import date, datetime, timezone
from threading import Lock
from typing import Protocol
from uuid import UUID, uuid4

from app.schemas.todo import Todo


class TodoRepository(Protocol):
    def list(self) -> list[Todo]:
        """created_at 오름차순으로 모든 Todo를 반환한다."""
        ...

    def get(self, todo_id: UUID) -> Todo | None: ...

    def create(self, title: str, due_date: date | None = None) -> Todo: ...

    def update(self, todo_id: UUID, changes: dict) -> Todo | None:
        """없는 id면 None을 반환한다."""
        ...

    def delete(self, todo_id: UUID) -> bool:
        """삭제했으면 True, 없는 id면 False를 반환한다."""
        ...


class InMemoryTodoRepository:
    """프로세스 메모리에 저장한다. 서버를 재시작하면 데이터가 사라진다."""

    def __init__(self) -> None:
        self._todos: dict[UUID, Todo] = {}
        # FastAPI는 동기 엔드포인트를 스레드 풀에서 실행하므로 동시 접근을 막는다.
        self._lock = Lock()

    def list(self) -> list[Todo]:
        with self._lock:
            # dict는 삽입 순서를 유지하고 sorted는 안정 정렬이라, 같은 시각이면 먼저 만든 것이 앞선다.
            return sorted(self._todos.values(), key=lambda t: t.created_at)

    def get(self, todo_id: UUID) -> Todo | None:
        with self._lock:
            return self._todos.get(todo_id)

    def create(self, title: str, due_date: date | None = None) -> Todo:
        todo = Todo(
            id=uuid4(),
            title=title,
            completed=False,
            created_at=datetime.now(timezone.utc),
            due_date=due_date,
        )
        with self._lock:
            self._todos[todo.id] = todo
        return todo

    def update(self, todo_id: UUID, changes: dict) -> Todo | None:
        with self._lock:
            current = self._todos.get(todo_id)
            if current is None:
                return None
            updated = current.model_copy(update=changes)
            self._todos[todo_id] = updated
            return updated

    def delete(self, todo_id: UUID) -> bool:
        with self._lock:
            return self._todos.pop(todo_id, None) is not None
