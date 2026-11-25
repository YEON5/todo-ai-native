"""/api/todos 라우터 (docs/api-spec.md API-001~004). HTTP 처리만 하고 로직은 Service에 맡긴다."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import get_todo_service
from app.schemas.todo import Todo, TodoCreate, TodoUpdate
from app.services.todo_service import TodoNotFoundError, TodoService

router = APIRouter(prefix="/api/todos", tags=["todos"])

NOT_FOUND = {404: {"description": "Todo not found"}}


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")


@router.get("", response_model=list[Todo], summary="API-001 목록 조회")
def list_todos(service: TodoService = Depends(get_todo_service)) -> list[Todo]:
    return service.list_todos()


@router.post(
    "",
    response_model=Todo,
    status_code=status.HTTP_201_CREATED,
    summary="API-002 생성",
)
def create_todo(
    data: TodoCreate, service: TodoService = Depends(get_todo_service)
) -> Todo:
    return service.create_todo(data)


@router.patch(
    "/{todo_id}", response_model=Todo, responses=NOT_FOUND, summary="API-003 수정"
)
def update_todo(
    todo_id: UUID, data: TodoUpdate, service: TodoService = Depends(get_todo_service)
) -> Todo:
    try:
        return service.update_todo(todo_id, data)
    except TodoNotFoundError:
        raise _not_found() from None


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=NOT_FOUND,
    summary="API-004 삭제",
)
def delete_todo(
    todo_id: UUID, service: TodoService = Depends(get_todo_service)
) -> Response:
    try:
        service.delete_todo(todo_id)
    except TodoNotFoundError:
        raise _not_found() from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)
