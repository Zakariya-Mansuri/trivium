import { useCallback, useEffect, useState } from 'react'
import { Button, Card, PageHeader, Spinner } from '../components/ui'
import { api } from '../lib/api'

interface Resource {
  title: string
  provider: string
  url: string
  type: string
  skill: string
}

interface Analysis {
  overall_score: number | null
  summary: string
  sub_scores: Record<string, number>
  strengths: string[]
  weaknesses: { area: string; evidence: string; tip: string }[]
}

interface SkillReportData {
  insufficient?: boolean
  message?: string
  report_type?: string
  computed_at?: string
  message_count?: number
  content?: {
    metrics: Record<string, number>
    analysis: Analysis
    resources: Resource[]
  }
}

interface Gap {
  topic: string
  unit_type: string
  reasons: string[]
  resources: Resource[]
}

const typeIcons: Record<string, string> = { course: '🎓', video: '▶', article: '📄', book: '📚', docs: '📘' }

function ResourceList({ resources }: { resources: Resource[] }) {
  return (
    <ul className="space-y-2">
      {resources.map((r) => (
        <li key={r.url}>
          <a
            href={r.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-start gap-2.5 rounded-lg border border-ink-700 bg-ink-800/60 px-3 py-2.5 hover:border-primary-600/50 transition-colors"
          >
            <span className="text-sm mt-0.5">{typeIcons[r.type] ?? '🔗'}</span>
            <span className="min-w-0">
              <span className="block text-sm text-ink-100 leading-snug">{r.title}</span>
              <span className="block text-xs text-ink-300 mt-0.5">
                {r.provider} · {r.type}
              </span>
            </span>
          </a>
        </li>
      ))}
    </ul>
  )
}

function scoreColor(v: number) {
  if (v >= 75) return 'text-good-500'
  if (v >= 50) return 'text-warn-500'
  return 'text-bad-500'
}

/** One self-contained report component — language and prompting are separate instances. */
function SkillReportCard({
  type,
  title,
  subtitle,
}: {
  type: 'language' | 'prompting'
  title: string
  subtitle: string
}) {
  const [report, setReport] = useState<SkillReportData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const load = useCallback(
    async (refresh = false) => {
      setBusy(true)
      setError(null)
      try {
        setReport(await api<SkillReportData>(`/skills/${type}${refresh ? '?refresh=true' : ''}`))
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to load report')
      } finally {
        setBusy(false)
      }
    },
    [type],
  )

  useEffect(() => {
    load()
  }, [load])

  return (
    <Card>
      <div className="flex items-start justify-between gap-3 mb-1">
        <div>
          <h2 className="font-display font-semibold text-ink-100">{title}</h2>
          <p className="text-xs text-ink-300 mt-0.5">{subtitle}</p>
        </div>
        <Button variant="secondary" onClick={() => load(true)} disabled={busy} className="!px-3 !py-1.5 text-xs">
          {busy ? 'Analyzing…' : 'Refresh'}
        </Button>
      </div>

      {error && <p className="text-sm text-bad-500 mt-4">{error}</p>}
      {!report && !error && <Spinner label="Analyzing your messages…" />}
      {report?.insufficient && <p className="text-sm text-ink-300 mt-4">{report.message}</p>}

      {report?.content && (
        <div className="mt-4 space-y-5">
          <div className="flex items-center gap-5">
            <p className={`font-display text-5xl font-bold ${scoreColor(report.content.analysis.overall_score ?? 0)}`}>
              {report.content.analysis.overall_score ?? '—'}
            </p>
            <p className="text-sm text-ink-200 leading-relaxed">{report.content.analysis.summary}</p>
          </div>

          <div className="space-y-2">
            {Object.entries(report.content.analysis.sub_scores).map(([dim, score]) => (
              <div key={dim} className="flex items-center gap-3 text-sm">
                <span className="w-32 text-ink-300 capitalize shrink-0">{dim.replace(/_/g, ' ')}</span>
                <div className="flex-1 h-2 rounded-full bg-ink-800 overflow-hidden">
                  <div
                    className={`h-full rounded-full ${score >= 75 ? 'bg-good-500' : score >= 50 ? 'bg-warn-500' : 'bg-bad-500'}`}
                    style={{ width: `${score}%` }}
                  />
                </div>
                <span className="w-8 text-right text-ink-200">{score}</span>
              </div>
            ))}
          </div>

          {report.content.analysis.strengths.length > 0 && (
            <div>
              <h3 className="text-xs uppercase tracking-widest text-ink-300 mb-2">Strengths</h3>
              <ul className="space-y-1 text-sm text-ink-200 list-disc list-inside">
                {report.content.analysis.strengths.map((s) => (
                  <li key={s}>{s}</li>
                ))}
              </ul>
            </div>
          )}

          {report.content.analysis.weaknesses.length > 0 && (
            <div>
              <h3 className="text-xs uppercase tracking-widest text-ink-300 mb-2">Areas to improve</h3>
              <div className="space-y-2.5">
                {report.content.analysis.weaknesses.map((w, i) => (
                  <div key={i} className="rounded-lg border border-ink-700 bg-ink-800/60 p-3">
                    <p className="text-sm text-ink-100 font-medium capitalize">{w.area.replace(/_/g, ' ')}</p>
                    {w.evidence && <p className="text-xs text-ink-300 mt-1">Seen in your messages: {w.evidence}</p>}
                    <p className="text-xs text-primary-300 mt-1.5">→ {w.tip}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div>
            <h3 className="text-xs uppercase tracking-widest text-ink-300 mb-2">Improve with (credible sources)</h3>
            <ResourceList resources={report.content.resources} />
          </div>

          <p className="text-[11px] text-ink-300">
            Based on {report.content.metrics.messages_analyzed} of your own messages · computed{' '}
            {report.computed_at ? new Date(report.computed_at).toLocaleString() : ''}
          </p>
        </div>
      )}
    </Card>
  )
}

export default function Skills() {
  const [gaps, setGaps] = useState<Gap[] | null>(null)

  useEffect(() => {
    api<{ gaps: Gap[] }>('/skills/recommendations').then((d) => setGaps(d.gaps))
  }, [])

  return (
    <div className="fade-up">
      <PageHeader
        title="Improve"
        subtitle="Evidence from your own sessions — how you write, how you prompt, and where your knowledge needs backup. Framed as growth, not a report card."
      />

      <div className="grid lg:grid-cols-2 gap-4 items-start mb-8">
        <SkillReportCard
          type="language"
          title="Language report"
          subtitle="Clarity, grammar, vocabulary, structure, tone — from your own messages."
        />
        <SkillReportCard
          type="prompting"
          title="Prompting report"
          subtitle="Context, specificity, constraints, output format, iteration — how you instruct AI."
        />
      </div>

      <h2 className="font-display font-semibold text-ink-100 mb-1">Fill your knowledge gaps</h2>
      <p className="text-sm text-ink-300 mb-4">
        Topics where your recall evidence is weakest, each paired with credible material (MIT OCW, Stanford,
        official docs, respected books).
      </p>
      {!gaps ? (
        <Spinner />
      ) : gaps.length === 0 ? (
        <Card>
          <p className="text-sm text-ink-300">
            No documented gaps yet — gaps appear when reviews reveal weak recall, stale concepts, or declining
            retention. Keep reviewing honestly.
          </p>
        </Card>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {gaps.map((g) => (
            <Card key={g.topic}>
              <p className="text-sm text-ink-100 font-medium">{g.topic}</p>
              <p className="text-xs text-warn-500 mt-1">{g.reasons.join(' · ')}</p>
              <div className="mt-3">
                <ResourceList resources={g.resources} />
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
