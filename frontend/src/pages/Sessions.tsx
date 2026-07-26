import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Badge, Button, Card, EmptyState, PageHeader, Spinner } from '../components/ui'
import { api } from '../lib/api'
import type { Project, Session } from '../lib/types'

function groupByRecency(sessions: Session[]): [string, Session[]][] {
  const now = new Date()
  const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
  const buckets: Record<string, Session[]> = { Today: [], Yesterday: [], 'This week': [], Earlier: [] }
  for (const s of sessions) {
    const t = new Date(s.started_at).getTime()
    if (t >= startOfDay) buckets.Today.push(s)
    else if (t >= startOfDay - 86_400_000) buckets.Yesterday.push(s)
    else if (t >= startOfDay - 6 * 86_400_000) buckets['This week'].push(s)
    else buckets.Earlier.push(s)
  }
  return Object.entries(buckets).filter(([, group]) => group.length > 0)
}

export default function Sessions() {
  const [params] = useSearchParams()
  const projectFilter = params.get('project')
  const [sessions, setSessions] = useState<Session[] | null>(null)
  const [projects, setProjects] = useState<Project[]>([])

  useEffect(() => {
    const query = projectFilter ? `?project_id=${projectFilter}` : ''
    Promise.all([api<Session[]>(`/sessions${query}`), api<Project[]>('/projects')]).then(([s, p]) => {
      setSessions(s)
      setProjects(p)
    })
  }, [projectFilter])

  const projectName = (id: string | null) => projects.find((p) => p.id === id)?.name ?? null

  return (
    <div className="fade-up">
      <PageHeader
        title="Sessions"
        subtitle={
          projectFilter
            ? `Sessions in ${projectName(projectFilter) ?? 'project'}`
            : 'Every captured coding session — native agent chats and imported transcripts.'
        }
        action={
          <Link to="/app/sessions/import">
            <Button>+ Import a session</Button>
          </Link>
        }
      />

      {sessions && sessions.length > 0 && (
        <p className="text-xs text-ink-300 -mt-2 mb-4">
          Sessions are learning material, not chat history — to continue a conversation, use the{' '}
          <Link to="/app/agent" className="text-primary-300 hover:text-primary-400">
            Agent
          </Link>
          's recent-chats panel.
        </p>
      )}
      {!sessions ? (
        <Spinner />
      ) : sessions.length === 0 ? (
        <EmptyState
          title="No sessions captured yet"
          hint="Chat with the native agent for full-fidelity capture, or paste a transcript from Claude Code, Cursor or Copilot."
          action={
            <div className="flex justify-center gap-3">
              <Link to="/app/agent">
                <Button>Open agent</Button>
              </Link>
              <Link to="/app/sessions/import">
                <Button variant="secondary">Import transcript</Button>
              </Link>
            </div>
          }
        />
      ) : (
        <div className="space-y-6">
          {groupByRecency(sessions).map(([label, group]) => (
            <section key={label}>
              <h2 className="text-xs uppercase tracking-widest text-ink-300 mb-2">{label}</h2>
              <div className="space-y-3">
                {group.map((s) => (
                  <Link key={s.id} to={`/app/sessions/${s.id}`} className="block">
                    <Card className="hover:border-primary-600/60 transition-colors !py-4">
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div className="min-w-0">
                          <p className="text-ink-100 font-medium truncate">{s.title ?? `${s.source_tool} session`}</p>
                          <p className="text-xs text-ink-300 mt-1">
                            {new Date(s.started_at).toLocaleString()}
                            {projectName(s.project_id) ? ` · ${projectName(s.project_id)}` : ''}
                            {` · via ${s.source_tool.replace(/_/g, ' ')}`}
                          </p>
                        </div>
                        <div className="flex gap-2 shrink-0 items-center">
                          <Badge label={s.source_fidelity} />
                          <Badge label={s.extraction_status} />
                          <span className="text-accent-400 text-xs" title="Generate learning artifacts">
                            ✦
                          </span>
                        </div>
                      </div>
                    </Card>
                  </Link>
                ))}
              </div>
            </section>
          ))}
        </div>
      )}
    </div>
  )
}
