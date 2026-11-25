import { useState, type FormEvent, type Ref } from 'react'
import type { NewTodo } from '../api/todos'
import { TITLE_MAX_LENGTH } from '../types'

interface TodoInputProps {
  // 저장에 성공하면 true. 실패하면 입력값을 그대로 남긴다 (AC-008-2).
  onAdd: (input: NewTodo) => Promise<boolean>
  inputRef?: Ref<HTMLInputElement>
  disabled?: boolean
}

export default function TodoInput({ onAdd, inputRef, disabled = false }: TodoInputProps) {
  const [text, setText] = useState('')
  const [dueDate, setDueDate] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    const trimmed = text.trim()
    if (!trimmed || submitting) return
    setSubmitting(true)
    const ok = await onAdd({ title: trimmed, due_date: dueDate || null })
    setSubmitting(false)
    if (ok) {
      setText('')
      setDueDate('')
    }
  }

  return (
    <form className="todo-input" onSubmit={handleSubmit}>
      <label htmlFor="new-todo" className="visually-hidden">
        할 일 입력
      </label>
      <input
        id="new-todo"
        ref={inputRef}
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="할 일을 입력하고 Enter"
        maxLength={TITLE_MAX_LENGTH}
        autoComplete="off"
        disabled={disabled}
      />
      <label htmlFor="new-todo-due" className="visually-hidden">
        마감일 (선택)
      </label>
      <input
        id="new-todo-due"
        className="date-input"
        type="date"
        value={dueDate}
        onChange={(e) => setDueDate(e.target.value)}
        title="마감일 (선택)"
        disabled={disabled}
      />
      <button
        type="submit"
        className="btn-primary"
        disabled={disabled || submitting || !text.trim()}
      >
        {submitting ? '추가 중' : '추가'}
      </button>
    </form>
  )
}
