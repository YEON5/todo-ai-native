"""의존성 연결. 저장소를 바꿀 때는 get_todo_repository만 수정한다 (TASK-S03)."""

from fastapi import Depends

from app.repositories.todo_repository import InMemoryTodoRepository, TodoRepository
from app.services.todo_service import TodoService

_repository = InMemoryTodoRepository()


def get_todo_repository() -> TodoRepository:
    return _repository


def get_todo_service(
    repository: TodoRepository = Depends(get_todo_repository),
) -> TodoService:
    return TodoService(repository)
