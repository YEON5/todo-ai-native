"""Todo 비즈니스 로직 (FR-001~005)."""

from uuid import UUID

from app.repositories.todo_repository import TodoRepository
from app.schemas.todo import Todo, TodoCreate, TodoUpdate


class TodoNotFoundError(Exception):
    def __init__(self, todo_id: UUID) -> None:
        super().__init__(f"Todo not found: {todo_id}")
        self.todo_id = todo_id


class TodoService:
    def __init__(self, repository: TodoRepository) -> None:
        self._repository = repository

    def list_todos(self) -> list[Todo]:
        return self._repository.list()

    def create_todo(self, data: TodoCreate) -> Todo:
        return self._repository.create(data.title, data.due_date)

    def update_todo(self, todo_id: UUID, data: TodoUpdate) -> Todo:
        updated = self._repository.update(todo_id, data.changes())
        if updated is None:
            raise TodoNotFoundError(todo_id)
        return updated

    def delete_todo(self, todo_id: UUID) -> None:
        if not self._repository.delete(todo_id):
            raise TodoNotFoundError(todo_id)
