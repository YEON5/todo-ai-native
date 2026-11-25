import type { Todo } from '../types'

interface ProgressSummaryProps {
  todos: Todo[]
}

// Above this count the per-task segments get too thin, so a continuous bar is drawn instead.
const MAX_SEGMENTS = 24

export default function ProgressSummary({ todos }: ProgressSummaryProps) {
  const total = todos.length
  const done = todos.filter((t) => t.completed).length
  const percent = total === 0 ? 0 : Math.round((done / total) * 100)

  const status =
    total === 0
      ? '첫 할 일을 추가해 보세요'
      : done === total
        ? `${total}개 모두 완료했어요`
        : `${total}개 중 ${done}개 완료`

  return (
    <section className="progress" aria-label="완료율">
      <div className="progress-figures">
        <span className="progress-percent">{percent}%</span>
        <span className="progress-status" aria-live="polite">
          {status}
        </span>
      </div>

      <div
        className="progress-track"
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={percent}
        aria-valuetext={`${percent}% 완료`}
      >
        {total === 0 ? (
          <span className="segment" />
        ) : total <= MAX_SEGMENTS ? (
          todos.map((t) => (
            <span key={t.id} className={`segment${t.completed ? ' filled' : ''}`} />
          ))
        ) : (
          <span className="bar">
            <span className="bar-fill" style={{ width: `${percent}%` }} />
          </span>
        )}
      </div>
    </section>
  )
}
