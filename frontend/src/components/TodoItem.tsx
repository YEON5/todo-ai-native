import { useEffect, useRef, useState, type FormEvent } from 'react'
import type { TodoChanges } from '../api/todos'
import { formatDueDate } from '../dates'
import { TITLE_MAX_LENGTH, type Todo } from '../types'

interface TodoItemProps {
  todo: Todo
  // 서버 요청 중이면 true. 이 동안 체크·수정·삭제를 다시 보내지 않는다.
  busy: boolean
  onToggle: (id: string) => void
  // 바뀐 필드만 받는다. 저장에 성공하면 true, 실패하면 편집 상태를 유지한다.
  onUpdate: (id: string, changes: TodoChanges) => Promise<boolean>
  onDelete: (id: string) => void
}

function PencilIcon() {
  return (
    <svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true">
      <path
        d="M13.6 3.4a1.9 1.9 0 0 1 2.7 2.7L7.1 15.3 3.5 16.5l1.2-3.6 8.9-9.5Z"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function TrashIcon() {
  return (
    <svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true">
      <path
        d="M4 6h12M8 6V4.5h4V6M5.5 6l.8 10h7.4l.8-10M8.5 9v4.5M11.5 9v4.5"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export default function TodoItem({ todo, busy, onToggle, onUpdate, onDelete }: TodoItemProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [draft, setDraft] = useState(todo.title)
  // 날짜 입력칸 값. 빈 문자열이면 마감일 없음.
  const [dueDraft, setDueDraft] = useState(todo.due_date ?? '')
  const [saving, setSaving] = useState(false)
  const editButtonRef = useRef<HTMLButtonElement>(null)
  const returnFocus = useRef(false)

  // After leaving edit mode, put keyboard focus back on the Edit button.
  useEffect(() => {
    if (!isEditing && returnFocus.current) {
      returnFocus.current = false
      editButtonRef.current?.focus()
    }
  }, [isEditing])

  const startEdit = () => {
    setDraft(todo.title)
    setDueDraft(todo.due_date ?? '')
    setIsEditing(true)
  }

  const finishEdit = () => {
    returnFocus.current = true
    setIsEditing(false)
  }

  const cancelEdit = () => {
    if (saving) return
    setDraft(todo.title)
    setDueDraft(todo.due_date ?? '')
    finishEdit()
  }

  const handleSave = async (e: FormEvent) => {
    e.preventDefault()
    const trimmed = draft.trim()
    if (!trimmed || saving) return
    // 바뀐 필드만 보낸다. 아무것도 안 바뀌었으면 요청 없이 편집을 끝낸다.
    const changes: TodoChanges = {}
    if (trimmed !== todo.title) changes.title = trimmed
    const nextDue = dueDraft || null
    if (nextDue !== todo.due_date) changes.due_date = nextDue
    if (Object.keys(changes).length === 0) {
      finishEdit()
      return
    }
    setSaving(true)
    const ok = await onUpdate(todo.id, changes)
    setSaving(false)
    if (ok) finishEdit()
  }

  // 요청 중에는 버튼을 disabled로 바꾸지 않는다. 포커스가 있는 요소를 disabled로 만들면
  // 포커스가 body로 사라지기 때문이다. 대신 aria-disabled를 표시하고 클릭을 무시한다.
  const guard = (action: () => void) => () => {
    if (!busy) action()
  }

  if (isEditing) {
    return (
      <li className="todo-card editing">
        {/* Esc는 제목·날짜 어느 입력칸에서 눌러도 취소한다. */}
        <form
          className="edit-form"
          onSubmit={handleSave}
          onKeyDown={(e) => e.key === 'Escape' && cancelEdit()}
        >
          <label htmlFor={`edit-${todo.id}`} className="visually-hidden">
            할 일 수정
          </label>
          <input
            id={`edit-${todo.id}`}
            type="text"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            maxLength={TITLE_MAX_LENGTH}
            autoComplete="off"
            autoFocus
          />
          <label htmlFor={`edit-due-${todo.id}`} className="visually-hidden">
            마감일 (비우면 마감일 없음)
          </label>
          <input
            id={`edit-due-${todo.id}`}
            className="date-input"
            type="date"
            value={dueDraft}
            onChange={(e) => setDueDraft(e.target.value)}
            title="마감일 (비우면 마감일 없음)"
          />
          <div className="edit-actions">
            <button type="button" className="btn-ghost" onClick={cancelEdit} aria-disabled={saving}>
              취소
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={!draft.trim()}
              aria-disabled={saving}
            >
              {saving ? '저장 중' : '저장'}
            </button>
          </div>
        </form>
        <p className="edit-hint">Enter로 저장, Esc로 취소</p>
      </li>
    )
  }

  return (
    <li className={`todo-card${todo.completed ? ' completed' : ''}`} aria-busy={busy}>
      <input
        id={`todo-check-${todo.id}`}
        className="check"
        type="checkbox"
        checked={todo.completed}
        onChange={guard(() => onToggle(todo.id))}
        aria-disabled={busy}
      />
      <div className="todo-body">
        <label htmlFor={`todo-check-${todo.id}`} className="todo-text">
          {todo.title}
        </label>
        {todo.due_date && (
          <span className="todo-due">
            마감 <time dateTime={todo.due_date}>{formatDueDate(todo.due_date)}</time>
          </span>
        )}
      </div>
      <div className="todo-actions">
        <button
          ref={editButtonRef}
          type="button"
          className="icon-btn"
          onClick={guard(startEdit)}
          aria-disabled={busy}
          aria-label={`'${todo.title}' 수정`}
          title="수정"
        >
          <PencilIcon />
        </button>
        <button
          type="button"
          className="icon-btn danger"
          onClick={guard(() => onDelete(todo.id))}
          aria-disabled={busy}
          aria-label={`'${todo.title}' 삭제`}
          title="삭제"
        >
          <TrashIcon />
        </button>
      </div>
    </li>
  )
}
