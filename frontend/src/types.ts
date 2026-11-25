// API 응답의 Todo 객체와 같은 모양이다 (docs/api-spec.md API-000).
export interface Todo {
  id: string
  title: string
  completed: boolean
  created_at: string
  // 마감일 'YYYY-MM-DD', 없으면 null (FR-009)
  due_date: string | null
}

// 제목 최대 길이. 백엔드 검증·DB CHECK와 같은 값이다 (R-04).
export const TITLE_MAX_LENGTH = 200
