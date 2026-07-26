import { useEffect, useState } from 'react'
import { Card, PageHeader, Spinner } from '../components/ui'
import { api } from '../lib/api'
import type { ActivityDay, EngagementMetrics, IndependenceMetrics, RetentionMetrics } from '../lib/types'

const BUCKET_LABELS: Record<string, string> = {
  day_1: 'Day 1-2',
  day_7: 'Day 3-10',
  day_30: 'Day 11-45',
  day_90: 'Day 46+',
}

/** Single-series bar chart: recall accuracy per day-offset bucket (magnitude → bars). */
function RetentionChart({ data }: { data: RetentionMetrics }) {
  const buckets = data.curve
  const width = 460
  const height = 210
  const pad = { top: 18, right: 12, bottom: 30, left: 40 }
  const innerW = width - pad.left - pad.right
  const innerH = height - pad.top - pad.bottom
  const barW = Math.min(56, (innerW / buckets.length) * 0.55)

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full" role="img" aria-label="Recall accuracy by review delay">
      {[0, 0.5, 1].map((t) => (
        <g key={t}>
          <line
            x1={pad.left}
            x2={width - pad.right}
            y1={pad.top + innerH * (1 - t)}
            y2={pad.top + innerH * (1 - t)}
            stroke="#1f2940"
            strokeWidth="1"
          />
          <text x={pad.left - 8} y={pad.top + innerH * (1 - t) + 4} textAnchor="end" fontSize="10" fill="#8a97b1">
            {Math.round(t * 100)}%
          </text>
        </g>
      ))}
      {buckets.map((b, i) => {
        const cx = pad.left + (innerW / buckets.length) * (i + 0.5)
        const value = b.accuracy
        const h = value === null ? 0 : Math.max(innerH * value, value > 0 ? 3 : 0)
        return (
          <g key={b.bucket}>
            {value !== null ? (
              <>
                <rect
                  x={cx - barW / 2}
                  y={pad.top + innerH - h}
                  width={barW}
                  height={h}
                  rx="4"
                  fill="#8098f9"
                >
                  <title>{`${BUCKET_LABELS[b.bucket]}: ${Math.round(value * 100)}% recall over ${b.reviews} reviews`}</title>
                </rect>
                <text x={cx} y={pad.top + innerH - h - 6} textAnchor="middle" fontSize="11" fill="#e3e8f2">
                  {Math.round(value * 100)}%
                </text>
              </>
            ) : (
              <text x={cx} y={pad.top + innerH - 8} textAnchor="middle" fontSize="10" fill="#8a97b1">
                no data
              </text>
            )}
            <text x={cx} y={height - 10} textAnchor="middle" fontSize="10" fill="#8a97b1">
              {BUCKET_LABELS[b.bucket]}
            </text>
          </g>
        )
      })}
    </svg>
  )
}

/** GitHub-style activity heatmap: sequential single-hue ramp, light→dark = more reviews. */
function ActivityHeatmap({ days, totalDays }: { days: ActivityDay[]; totalDays: number }) {
  const byDate = new Map(days.map((d) => [d.date, d]))
  const today = new Date()
  const cells: { date: string; reviews: number }[] = []
  for (let i = totalDays - 1; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(today.getDate() - i)
    const key = d.toISOString().slice(0, 10)
    cells.push({ date: key, reviews: byDate.get(key)?.reviews ?? 0 })
  }
  const weeks: (typeof cells)[] = []
  for (let i = 0; i < cells.length; i += 7) weeks.push(cells.slice(i, i + 7))
  const max = Math.max(1, ...cells.map((c) => c.reviews))
  const ramp = ['#161d2e', '#33437c', '#3d54a8', '#6172f3', '#a4bcfd'] // sequential: surface → light indigo
  const color = (n: number) => (n === 0 ? ramp[0] : ramp[Math.min(4, 1 + Math.floor((n / max) * 3.999))])
  const size = 13
  const gap = 3

  return (
    <div>
      <svg
        width={weeks.length * (size + gap)}
        height={7 * (size + gap)}
        role="img"
        aria-label="Daily review activity"
        className="max-w-full"
      >
        {weeks.map((week, wi) =>
          week.map((cell, di) => (
            <rect
              key={cell.date}
              x={wi * (size + gap)}
              y={di * (size + gap)}
              width={size}
              height={size}
              rx="3"
              fill={color(cell.reviews)}
              stroke={cell.reviews === 0 ? '#1f2940' : 'none'}
              strokeWidth="1"
            >
              <title>{`${cell.date}: ${cell.reviews} review${cell.reviews === 1 ? '' : 's'}`}</title>
            </rect>
          )),
        )}
      </svg>
      <div className="flex items-center gap-1.5 mt-3 text-xs text-ink-300">
        Less
        {ramp.map((c) => (
          <span key={c} className="inline-block h-3 w-3 rounded-[3px]" style={{ backgroundColor: c, border: c === ramp[0] ? '1px solid #1f2940' : 'none' }} />
        ))}
        More
      </div>
    </div>
  )
}

export default function Metrics() {
  const [engagement, setEngagement] = useState<EngagementMetrics | null>(null)
  const [retention, setRetention] = useState<RetentionMetrics | null>(null)
  const [activity, setActivity] = useState<ActivityDay[] | null>(null)
  const [independence, setIndependence] = useState<IndependenceMetrics | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      api<EngagementMetrics>('/metrics/engagement'),
      api<RetentionMetrics>('/metrics/retention'),
      api<ActivityDay[]>('/metrics/activity?days=91'),
      api<IndependenceMetrics>('/metrics/independence'),
    ])
      .then(([e, r, a, i]) => {
        setEngagement(e)
        setRetention(r)
        setActivity(a)
        setIndependence(i)
      })
      .catch((e) => setError(e.message))
  }, [])

  if (error) return <p className="text-bad-500">{error}</p>
  if (!engagement || !retention || !activity || !independence) return <Spinner label="Crunching your numbers…" />

  const tiles = [
    {
      label: 'Overall recall rate',
      value: retention.overall_recall_rate !== null ? `${Math.round(retention.overall_recall_rate * 100)}%` : '—',
      hint: `${retention.total_reviews} graded recalls`,
    },
    {
      label: 'Learn actions',
      value: engagement.event_counts.learn_triggered ?? 0,
      hint: `across ${engagement.total_sessions} sessions`,
    },
    {
      label: 'Artifacts completed',
      value: engagement.event_counts.artifact_completed ?? 0,
      hint: 'recall-based completions',
    },
    {
      label: 'AI-assist ratio',
      value: independence.ai_assist_ratio !== null ? `${Math.round(independence.ai_assist_ratio * 100)}%` : '—',
      hint: `last ${independence.window_days} days · lower = more independent`,
    },
  ]

  return (
    <div className="fade-up">
      <PageHeader
        title="Metrics"
        subtitle="Trends, not report cards. Retention is measured from graded recall only — the same evidence your profile is built on."
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {tiles.map((t) => (
          <Card key={t.label}>
            <p className="font-display text-3xl font-bold text-ink-100">{t.value}</p>
            <p className="text-sm text-ink-200 mt-1">{t.label}</p>
            <p className="text-xs text-ink-300 mt-0.5">{t.hint}</p>
          </Card>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-4 mb-6">
        <Card>
          <h2 className="font-display font-semibold text-ink-100 mb-1">Retention curve</h2>
          <p className="text-xs text-ink-300 mb-4">
            Recall accuracy vs how long after learning the review happened. Holding steady at longer delays is the win.
          </p>
          {retention.total_reviews === 0 ? (
            <p className="text-sm text-ink-300 py-10 text-center">Complete reviews to see your curve.</p>
          ) : (
            <RetentionChart data={retention} />
          )}
        </Card>

        <Card>
          <h2 className="font-display font-semibold text-ink-100 mb-1">Review activity</h2>
          <p className="text-xs text-ink-300 mb-4">
            {activity.reduce((sum, d) => sum + d.reviews, 0)} reviews in the last 13 weeks.
          </p>
          <ActivityHeatmap days={activity} totalDays={91} />
        </Card>
      </div>

      <Card>
        <h2 className="font-display font-semibold text-ink-100 mb-1">Independence (Layer 3 — early)</h2>
        <p className="text-xs text-ink-300 mb-4">{independence.note}</p>
        <div className="flex items-center gap-4 max-w-md">
          <span className="text-xs text-ink-300 w-24 shrink-0">You wrote</span>
          <div className="flex-1 h-3 rounded-full bg-ink-800 overflow-hidden flex">
            <div
              className="h-full bg-good-500"
              style={{ width: `${independence.ai_assist_ratio === null ? 0 : Math.round((1 - independence.ai_assist_ratio) * 100)}%` }}
            />
            <div
              className="h-full bg-primary-500"
              style={{ width: `${independence.ai_assist_ratio === null ? 0 : Math.round(independence.ai_assist_ratio * 100)}%` }}
            />
          </div>
          <span className="text-xs text-ink-300 w-24 shrink-0 text-right">AI wrote</span>
        </div>
        {independence.ai_assist_ratio === null && (
          <p className="text-sm text-ink-300 mt-3">No code-bearing messages in this window yet.</p>
        )}
      </Card>
    </div>
  )
}
