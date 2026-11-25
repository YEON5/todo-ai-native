// /api/todos 호출 모듈 (docs/api-spec.md). 컴포넌트에서 fetch를 직접 쓰지 않고 이 모듈을 거친다.
import type { Todo } from '../types'

const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/$/, '')
const TODOS_URL = `${BASE_URL}/api/todos`

export class ApiError extends Error {
  // status가 없으면 서버에 닿지 못한 경우(네트워크 오류, 서버 꺼짐)다.
  readonly status?: number

  constructor(message: string, status?: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(url, {
      ...init,
      headers: init?.body ? { 'Content-Type': 'application/json' } : undefined,
    })
  } catch {
    throw new ApiError('서버에 연결할 수 없어요')
  }

  if (!response.ok) {
    throw new ApiError(`요청이 실패했어요 (${response.status})`, response.status)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}

export function listTodos(): Promise<Todo[]> {
  return request<Todo[]>(TODOS_URL)
}

export type NewTodo = Pick<Todo, 'title' | 'due_date'>

export function createTodo(input: NewTodo): Promise<Todo> {
  return request<Todo>(TODOS_URL, { method: 'POST', body: JSON.stringify(input) })
}

// due_date: null은 마감일 지우기다 (API-003).
export type TodoChanges = Partial<Pick<Todo, 'title' | 'completed' | 'due_date'>>

export function updateTodo(id: string, changes: TodoChanges): Promise<Todo> {
  return request<Todo>(`${TODOS_URL}/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(changes),
  })
}

export function deleteTodo(id: string): Promise<void> {
  return request<void>(`${TODOS_URL}/${id}`, { method: 'DELETE' })
}
