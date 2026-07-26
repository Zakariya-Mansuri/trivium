import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import ArtifactPlayer from '../components/ArtifactPlayer'
import { Badge, Button, Card, ErrorNote, PageHeader, Spinner } from '../components/ui'
import { api } from '../lib/api'
import type { KnowledgeUnit, LearnResponse, SessionDetail as SessionDetailType } from '../lib/types'

export default function SessionDetail() {
  const { id } = useParams()
  const [session, setSession] = useState<SessionDetailType | null>(null)
  const [units, setUnits] = useState<KnowledgeUnit[]>([])
  const [learn, setLearn] = useState<LearnResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const load = useCallback(async () => {
    const [s, u] = await Promise.all([
      api<SessionDetailType>(`/sessions/${id}`),
      api<KnowledgeUnit[]>(`/knowledge-units?session_id=${id}`),
    ])
    setSession(s)
    setUnits(u)
  }, [id])

  useEffect(() => {
    load().catch((e) => setError(e.message))
  }, [load])

  const triggerLearn = async (messageId?: string) => {
    setBusy(true)
    setError(null)
    setLearn(null)
    try {
      const resp = await api<LearnResponse>('/learn', {
        method: 'POST',
        body: messageId
          ? { scope_type: 'message', message_id: messageId }
          : { scope_type: 'chat', session_id: id },
      })
      setLearn(resp)
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Learn failed')
    } finally {
      setBusy(false)
    }
  }

  const reExtract = async () => {
    setBusy(true)
    try {
      await api(`/sessions/${id}/extract`, { method: 'POST' })
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Extraction failed')
    } finally {
      setBusy(false)
    }
  }

  if (error && !session) return <p className="text-bad-500">{error}</p>
  if (!session) return <Spinner />

  return (
    <div className="fade-up">
      <PageHeader
        title={session.title ?? `${session.source_tool} session`}
        subtitle={`${new Date(session.started_at).toLocaleString()} · via ${session.source_tool.replace(/_/g, ' ')}`}
        action={
          <div className="flex gap-2">
            <Button variant="secondary" onClick={reExtract} disabled={busy || session.extraction_status === 'running'}>
              Re-extract
            </Button>
            <Button onClick={() => triggerLearn()} disabled={busy}>
              {busy ? 'Generating…' : '✦ Learn this chat'}
            </Button>
          </div>
        }
      />
      <div className="flex gap-2 mb-6">
        <Badge label={session.source_fidelity} />
        <Badge label={session.extraction_status} />
        {session.source_fidelity === 'wrapped' && (
          <span className="text-xs text-ink-300 self-center">
            Imported session — capture fidelity is lower than the native agent's.
          </span>
        )}
      </div>

      <ErrorNote message={error} />

      {learn && (
        <Card className="mb-6 border-primary-600/50">
          <h2 className="font-display font-semibold text-ink-100 mb-1">Learning artifacts</h2>
          {learn.message ? (
            <p className="text-sm text-warn-500">{learn.message}</p>
          ) : (
            <>
              <p className="text-xs text-ink-300 mb-5">
                Covering {learn.units_covered} knowledge unit{learn.units_covered === 1 ? '' : 's'} — practice now,
                graded reviews unlock after the consolidation window.
              </p>
              <div className="space-y-6">
                {learn.artifacts.map((a) => (
                  <div key={a.id} className="border-t border-ink-700 pt-5 first:border-0 first:pt-0">
                    <ArtifactPlayer artifact={a} mode="learn" />
                  </div>
                ))}
              </div>
            </>
          )}
        </Card>
      )}

      <div className="grid lg:grid-cols-[1fr_320px] gap-6 items-start">
        <div className="space-y-3">
          {session.messages.map((m) => (
            <div
              key={m.id}
              className={`rounded-xl border p-4 ${
                m.role === 'user' ? 'bg-ink-800 border-ink-600 ml-6' : 'bg-ink-900 border-ink-700 mr-6'
              }`}
            >
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="text-xs font-medium text-ink-300 uppercase tracking-wide">
                  {m.role} {m.authored_by ? `· authored by ${m.authored_by}` : ''}
                </span>
                <button
                  onClick={() => triggerLearn(m.id)}
                  className="text-xs text-accent-400 hover:text-accent-500"
                  disabled={busy}
                  title="Generate a learning artifact from just this message"
                >
                  ✦ Learn
                </button>
              </div>
              <p className="text-sm text-ink-100 whitespace-pre-wrap leading-relaxed">{m.content}</p>
              {m.code_diff && (
                <pre className="mt-3 rounded-lg bg-ink-950 border border-ink-700 p-3 text-xs text-ink-200 overflow-x-auto">
                  {m.code_diff}
                </pre>
              )}
            </div>
          ))}
        </div>

        <Card>
          <h2 className="font-display font-semibold text-ink-100 mb-3">Extracted knowledge</h2>
          {units.length === 0 ? (
            <p className="text-sm text-ink-300">
              {session.extraction_status === 'insufficient_content'
                ? 'Not enough substantive content in this session to extract from.'
                : 'No knowledge units yet — extraction may still be running.'}
            </p>
          ) : (
            <ul className="space-y-3">
              {units.map((u) => (
                <li key={u.id} className="border-b border-ink-800 pb-3 last:border-0 last:pb-0">
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm text-ink-100">{u.title}</p>
                    <Badge label={u.unit_type} />
                  </div>
                  {u.difficulty && <p className="text-xs text-ink-300 mt-1">{u.difficulty}</p>}
                </li>
              ))}
            </ul>
          )}
          <Link to="/app/profile" className="block text-xs text-primary-300 hover:text-primary-400 mt-4">
            See these in your Knowledge Profile →
          </Link>
        </Card>
      </div>
    </div>
  )
}
