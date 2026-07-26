import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import ArtifactPlayer from '../components/ArtifactPlayer'
import { Button, Card, ErrorNote, Input, PageHeader, Spinner } from '../components/ui'
import { api } from '../lib/api'
import type { Artifact, LearnResponse, Project, Session } from '../lib/types'

type Scope = 'chat' | 'project' | 'time_range'

export default function Learn() {
  const [params] = useSearchParams()
  const [scope, setScope] = useState<Scope>((params.get('scope') as Scope) || 'chat')
  const [projects, setProjects] = useState<Project[]>([])
  const [sessions, setSessions] = useState<Session[]>([])
  const [projectId, setProjectId] = useState(params.get('project') ?? '')
  const [sessionId, setSessionId] = useState('')
  const [timeStart, setTimeStart] = useState('')
  const [timeEnd, setTimeEnd] = useState('')
  const [result, setResult] = useState<LearnResponse | null>(null)
  const [history, setHistory] = useState<Artifact[] | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([api<Project[]>('/projects'), api<Session[]>('/sessions'), api<Artifact[]>('/artifacts?limit=10')]).then(
      ([p, s, a]) => {
        setProjects(p)
        setSessions(s)
        setHistory(a)
      },
    )
  }, [])

  const trigger = async () => {
    setBusy(true)
    setError(null)
    setResult(null)
    try {
      const body: Record<string, unknown> = { scope_type: scope }
      if (scope === 'chat') body.session_id = sessionId
      if (scope === 'project') body.project_id = projectId
      if (scope === 'time_range') {
        body.time_start = timeStart ? new Date(timeStart).toISOString() : null
        body.time_end = timeEnd ? new Date(timeEnd).toISOString() : null
      }
      const resp = await api<LearnResponse>('/learn', { method: 'POST', body })
      setResult(resp)
      setHistory(await api<Artifact[]>('/artifacts?limit=10'))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Learn failed')
    } finally {
      setBusy(false)
    }
  }

  const canTrigger =
    (scope === 'chat' && sessionId) || (scope === 'project' && projectId) || (scope === 'time_range' && timeStart && timeEnd)

  const scopes: { key: Scope; label: string; hint: string }[] = [
    { key: 'chat', label: 'A session', hint: 'One conversation' },
    { key: 'project', label: 'A project', hint: 'All its sessions' },
    { key: 'time_range', label: 'A time range', hint: 'Week, month, all-time' },
  ]

  return (
    <div className="fade-up">
      <PageHeader
        title="Learn"
        subtitle="Any span, any time — always on your initiative. The format is auto-selected per content type, and every choice is logged."
      />

      <Card className="mb-8">
        <div className="flex flex-wrap gap-2 mb-5">
          {scopes.map((s) => (
            <button
              key={s.key}
              onClick={() => setScope(s.key)}
              className={`rounded-lg border px-4 py-2.5 text-sm text-left transition-colors ${
                scope === s.key
                  ? 'border-primary-500 bg-primary-600/15 text-primary-300'
                  : 'border-ink-600 text-ink-200 hover:bg-ink-800'
              }`}
            >
              <span className="block font-medium">{s.label}</span>
              <span className="block text-xs opacity-70">{s.hint}</span>
            </button>
          ))}
        </div>

        <div className="grid sm:grid-cols-2 gap-4 mb-5">
          {scope === 'chat' && (
            <div>
              <label className="text-xs text-ink-300 block mb-1.5">Session</label>
              <select
                value={sessionId}
                onChange={(e) => setSessionId(e.target.value)}
                className="w-full rounded-lg bg-ink-800 border border-ink-600 px-3 py-2 text-sm text-ink-100 outline-none focus:border-primary-500"
              >
                <option value="">Choose a session…</option>
                {sessions.map((s) => (
                  <option key={s.id} value={s.id}>
                    {(s.title ?? s.source_tool).slice(0, 60)} — {new Date(s.started_at).toLocaleDateString()}
                  </option>
                ))}
              </select>
            </div>
          )}
          {scope === 'project' && (
            <div>
              <label className="text-xs text-ink-300 block mb-1.5">Project</label>
              <select
                value={projectId}
                onChange={(e) => setProjectId(e.target.value)}
                className="w-full rounded-lg bg-ink-800 border border-ink-600 px-3 py-2 text-sm text-ink-100 outline-none focus:border-primary-500"
              >
                <option value="">Choose a project…</option>
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>
          )}
          {scope === 'time_range' && (
            <>
              <div>
                <label className="text-xs text-ink-300 block mb-1.5">From</label>
                <Input type="date" value={timeStart} onChange={(e) => setTimeStart(e.target.value)} />
              </div>
              <div>
                <label className="text-xs text-ink-300 block mb-1.5">To</label>
                <Input type="date" value={timeEnd} onChange={(e) => setTimeEnd(e.target.value)} />
              </div>
            </>
          )}
        </div>

        <ErrorNote message={error} />
        <Button onClick={trigger} disabled={!canTrigger || busy}>
          {busy ? 'Generating artifacts…' : '✦ Generate learning artifacts'}
        </Button>
      </Card>

      {result && (
        <div className="mb-8">
          {result.message ? (
            <Card className="border-warn-500/40">
              <p className="text-sm text-warn-500">{result.message}</p>
            </Card>
          ) : (
            <div className="space-y-5">
              <p className="text-sm text-ink-300">
                {result.artifacts.length} artifact{result.artifacts.length === 1 ? '' : 's'} covering{' '}
                {result.units_covered} knowledge units:
              </p>
              {result.artifacts.map((a) => (
                <Card key={a.id}>
                  <ArtifactPlayer artifact={a} mode="learn" />
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      <h2 className="font-display font-semibold text-ink-100 mb-3">Recent artifacts</h2>
      {!history ? (
        <Spinner />
      ) : history.length === 0 ? (
        <p className="text-sm text-ink-300">Nothing generated yet — trigger your first Learn above.</p>
      ) : (
        <div className="space-y-2">
          {history.map((a) => (
            <div key={a.id} className="card !py-3 px-4 flex items-center justify-between gap-3 text-sm">
              <span className="text-ink-200">
                {a.format.replace(/_/g, ' ')} · {a.scope_type.replace(/_/g, ' ')} scope
              </span>
              <span className="text-xs text-ink-300">{new Date(a.generated_at).toLocaleString()}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
