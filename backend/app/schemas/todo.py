"""Todo 요청·응답 모델 (docs/api-spec.md API-000)."""

import re
from datetime import date, datetime
from typing import Annotated, Any
from uuid import UUID

from pydantic import (
    BaseModel,
    BeforeValidator,
    StrictBool,
    StringConstraints,
    model_validator,
)

TITLE_MAX_LENGTH = 200

# 앞뒤 공백을 제거한 뒤 1~200자 (R-04). DB CHECK 제약과 같은 규칙이다.
Title = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=TITLE_MAX_LENGTH),
]

_DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")


def _require_iso_date_string(value: Any) -> Any:
    """마감일은 정확히 'YYYY-MM-DD' 문자열만 받는다 (FR-009, R-17).

    Pydantic 기본 모드는 숫자(유닉스 시간)나 '2026-11-28T00:00:00'도 날짜로 바꾸므로,
    날짜로 변환하기 전에 형식을 먼저 검사한다. 없는 날짜(2026-02-30)는 이후 date 변환에서 거부된다.
    """
    if value is None or isinstance(value, date):
        return value
    if not isinstance(value, str) or not _DATE_PATTERN.fullmatch(value):
        raise ValueError("마감일은 YYYY-MM-DD 형식의 문자열이어야 합니다")
    return value


DueDate = Annotated[date | None, BeforeValidator(_require_iso_date_string)]


class TodoCreate(BaseModel):
    """API-002 요청. title·due_date 외의 필드(id, completed, created_at)는 무시한다."""

    title: Title
    due_date: DueDate = None


class TodoUpdate(BaseModel):
    """API-003 요청. 보낸 필드만 바꾸며, 하나 이상 있어야 한다."""

    title: Title | None = None
    completed: StrictBool | None = None
    # null은 '마감일 지우기'라는 뜻이라 허용한다 (R-15).
    due_date: DueDate = None

    @model_validator(mode="after")
    def check_fields(self) -> "TodoUpdate":
        if not self.model_fields_set:
            raise ValueError("title, completed, due_date 중 하나 이상을 보내야 합니다")
        for name in self.model_fields_set - {"due_date"}:
            if getattr(self, name) is None:
                raise ValueError(f"{name}에는 null을 보낼 수 없습니다")
        return self

    def changes(self) -> dict:
        return self.model_dump(exclude_unset=True)


class Todo(BaseModel):
    """API 응답의 Todo 객체."""

    id: UUID
    title: str
    completed: bool
    created_at: datetime
    due_date: date | None = None
