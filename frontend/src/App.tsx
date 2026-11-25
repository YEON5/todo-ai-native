import { useCallback, useEffect, useRef, useState } from 'react'
import * as api from './api/todos'
import ProgressSummary from './components/ProgressSummary'
import TodoInput from './components/TodoInput'
import TodoItem from './components/TodoItem'
import type { Todo } from './types'

const today = new Intl.DateTimeFormat('ko-KR', {
  month: 'long',
  day: 'numeric',
  weekday: 'long',
}).format(new Date())

type LoadState = 'loading' | 'ready' | 'error'

// 서버 응답이 성공한 뒤에만 화면 상태를 바꾼다 (PRD 6장, 비관적 갱신).
export default function App() {
  const [todos, setTodos] = useState<Todo[]>([])
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [actionError, setActionError] = useState<string | null>(null)
  const [busyIds, setBusyIds] = useState<ReadonlySet<string>>(new Set())
  const inputRef = useRef<HTMLInputElement>(null)
  // Where keyboard focus goes after a delete: the next task's checkbox, or the input.
  const focusAfterDelete = useRef<string | null | undefined>(undefined)

  // 목록 조회 결과를 상태에 반영한다. 서버 응답이 온 뒤(비동기 콜백)에만 호출된다.
  const applyList = useCallback((list: Todo[]) => {
    setTodos(list)
    setLoadState('ready')
  }, [])

  const load = useCallback(() => {
    setLoadState('loading')
    api.listTodos().then(applyList, () => setLoadState('error'))
  }, [applyList])

  useEffect(() => {
    // 처음 열 때 한 번 목록을 불러온다 (FR-002). 초기 상태가 이미 'loading'이다.
    let cancelled = false
    api.listTodos().then(
      (list) => {
        if (!cancelled) applyList(list)
      },
      () => {
        if (!cancelled) setLoadState('error')
      },
    )
    return () => {
      cancelled = true
    }
  }, [applyList])

  useEffect(() => {
    const target = focusAfterDelete.current
    if (target === undefined) return
    focusAfterDelete.current = undefined
    const el = target ? document.getElementById(`todo-check-${target}`) : null
    ;(el ?? inputRef.current)?.focus()
  }, [todos])

  const setBusy = (id: string, busy: boolean) => {
    setBusyIds((prev) => {
      const next = new Set(prev)
      if (busy) next.add(id)
      else next.delete(id)
      return next
    })
  }

  const replaceTodo = (updated: Todo) => {
    setTodos((prev) => prev.map((t) => (t.id === updated.id ? updated : t)))
  }

  const addTodo = async (input: api.NewTodo): Promise<boolean> => {
    try {
      const created = await api.createTodo(input)
      setTodos((prev) => [...prev, created])
      setActionError(null)
      return true
    } catch {
      setActionError('할 일을 추가하지 못했어요. 서버 연결을 확인한 뒤 다시 추가해 주세요.')
      return false
    }
  }

  const toggleTodo = async (id: string) => {
    const todo = todos.find((t) => t.id === id)
    if (!todo) return
    setBusy(id, true)
    try {
      replaceTodo(await api.updateTodo(id, { completed: !todo.completed }))
      setActionError(null)
    } catch {
      setActionError('완료 상태를 바꾸지 못했어요. 다시 시도해 주세요.')
    } finally {
      setBusy(id, false)
    }
  }

  const updateTodo = async (id: string, changes: api.TodoChanges): Promise<boolean> => {
    setBusy(id, true)
    try {
      replaceTodo(await api.updateTodo(id, changes))
      setActionError(null)
      return true
    } catch {
      setActionError('수정한 내용을 저장하지 못했어요. 다시 저장해 주세요.')
      return false
    } finally {
      setBusy(id, false)
    }
  }

  const deleteTodo = async (id: string) => {
    setBusy(id, true)
    try {
      await api.deleteTodo(id)
      setActionError(null)
      // 서버 응답 시점의 목록을 기준으로 다음 포커스 대상을 정한다.
      setTodos((prev) => {
        const index = prev.findIndex((t) => t.id === id)
        const next = prev[index + 1] ?? prev[index - 1]
        focusAfterDelete.current = next?.id ?? null
        return prev.filter((t) => t.id !== id)
      })
    } catch (error) {
      if (error instanceof api.ApiError && error.status === 404) {
        // 이미 다른 곳에서 삭제됨: 서버 목록과 다시 맞춘다.
        setActionError('이미 삭제된 할 일이에요. 목록을 새로 불러왔어요.')
        load()
      } else {
        setActionError('할 일을 삭제하지 못했어요. 다시 시도해 주세요.')
      }
    } finally {
      setBusy(id, false)
    }
  }

  return (
    <main className="app">
      <header className="app-header">
        <p className="app-date">{today}</p>
        <h1>My ToDo</h1>
      </header>

      {loadState === 'ready' && <ProgressSummary todos={todos} />}

      <TodoInput onAdd={addTodo} inputRef={inputRef} disabled={loadState !== 'ready'} />

      {actionError && (
        <div className="alert" role="alert">
          <p>{actionError}</p>
          <button type="button" className="btn-ghost" onClick={() => setActionError(null)}>
            닫기
          </button>
        </div>
      )}

      {loadState === 'loading' && (
        <p className="status" role="status">
          할 일을 불러오는 중이에요.
        </p>
      )}

      {loadState === 'error' && (
        <div className="status status-error" role="alert">
          <p>할 일을 불러오지 못했어요. 서버가 실행 중인지 확인해 주세요.</p>
          <button type="button" className="btn-primary" onClick={load}>
            다시 시도
          </button>
        </div>
      )}

      {loadState === 'ready' &&
        (todos.length === 0 ? (
          <p className="empty">아직 할 일이 없어요.</p>
        ) : (
          <ul className="todo-list" aria-label="할 일 목록">
            {todos.map((todo) => (
              <TodoItem
                key={todo.id}
                todo={todo}
                busy={busyIds.has(todo.id)}
                onToggle={toggleTodo}
                onUpdate={updateTodo}
                onDelete={deleteTodo}
              />
            ))}
          </ul>
        ))}
    </main>
  )
}
