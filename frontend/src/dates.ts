// 마감일(YYYY-MM-DD) 표시 변환 (FR-009, R-16).
// new Date('2026-11-28')은 UTC 자정으로 해석되어 시간대에 따라 하루가 밀리므로,
// 연·월·일로 나눠 로컬 날짜로 만든다.

const WEEKDAY = new Intl.DateTimeFormat('ko-KR', { weekday: 'short' })

function toLocalDate(isoDate: string): Date {
  const [year, month, day] = isoDate.split('-').map(Number)
  return new Date(year, month - 1, day)
}

/** '2026-11-28' → '11월 28일 (토)'. 올해가 아니면 연도를 붙인다. */
export function formatDueDate(isoDate: string): string {
  const date = toLocalDate(isoDate)
  const label = `${date.getMonth() + 1}월 ${date.getDate()}일 (${WEEKDAY.format(date)})`
  return date.getFullYear() === new Date().getFullYear()
    ? label
    : `${date.getFullYear()}년 ${label}`
}
