import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Badge, Card, PageHeader, Spinner } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import { api } from '../lib/api'
import type { Profile, ReviewQueue, Session } from '../lib/types'

export default function Dashboard() {
  const { user } = useAuth()
  const [queue, setQueue] = useState<ReviewQueue | null>(null)
  const [profile, setProfile] = useState<Profile | null>(null)
  const [sessions, setSessions] = useState<Session[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([api<ReviewQueue>('/reviews/queue'), api<Profile>('/profile'), api<Session[]>('/sessions')])
      .then(([q, p, s]) => {
        setQueue(q)
        setProfile(p)
        setSessions(s)
      })
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load'))
  }, [])

  if (error) return <p className="text-bad-500">{error}</p>
  if (!queue || !profile || !sessions) return <Spinner label="Loading your knowledge…" />

  const counts = profile.counts
  const stats = [
    { label: 'Due for review', value: queue.total_due, to: '/app/review', accent: queue.total_due > 0 },
    { label: 'Concepts tracked', value: profile.entries.length, to: '/app/profile' },
    { label: 'Consolidated', value: counts.consolidated ?? 0, to: '/app/profile' },
    { label: 'Sessions captured', value: sessions.length, to: '/app/sessions' },
  ]

  return (
    <div className="fade-up">
      <PageHeader
        title={`Welcome back${user?.display_name ? `, ${user.display_name}` : ''}`}
        subtitle="Here's where your knowledge stands today."
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((s) => (
          <Link key={s.label} to={s.to}>
            <Card className={`hover:border-primary-600/60 transition-colors ${s.accent ? 'border-accent-500/50' : ''}`}>
              <p className={`font-display text-3xl font-bold ${s.accent ? 'text-accent-400' : 'text-ink-100'}`}>{s.value}</p>
              <p className="text-sm text-ink-300 mt-1">{s.label}</p>
            </Card>
          </Link>
        ))}
      </div>

      {queue.total_due > 0 ? (
        <Card className="mb-8 border-accent-500/40 bg-accent-500/5">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="font-display font-semibold text-ink-100">
                {queue.total_due} concept{queue.total_due === 1 ? '' : 's'} ready for recall
              </h2>
              <p className="text-sm text-ink-300 mt-1">
                Interleaved across {Math.max(queue.projects_in_session, 1)} project
                {queue.projects_in_session === 1 ? '' : 's'} — spacing and mixing are deliberate.
              </p>
            </div>
            <Link to="/app/review" className="rounded-lg bg-primary-600 hover:bg-primary-500 px-5 py-2.5 text-sm font-medium text-white">
              Start review session
            </Link>
          </div>
        </Card>
      ) : (
        <Card className="mb-8">
          <h2 className="font-display font-semibold text-ink-100">Nothing due right now</h2>
          <p className="text-sm text-ink-300 mt-1">
            {queue.next_due_at
              ? `Next review unlocks ${new Date(queue.next_due_at).toLocaleString()}. The delay is the point — spaced beats crammed.`
              : 'Capture a coding session, then trigger Learn to start building your review queue.'}
          </p>
        </Card>
      )}

      <div className="grid lg:grid-cols-2 gap-4">
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display font-semibold text-ink-100">Recent sessions</h2>
            <Link to="/app/sessions" className="text-xs text-primary-300 hover:text-primary-400">
              View all →
            </Link>
          </div>
          {sessions.length === 0 ? (
            <p className="text-sm text-ink-300">
              No sessions yet. <Link to="/app/agent" className="text-primary-300">Chat with the agent</Link> or{' '}
              <Link to="/app/sessions" className="text-primary-300">import one</Link>.
            </p>
          ) : (
            <ul className="space-y-3">
              {sessions.slice(0, 5).map((s) => (
                <li key={s.id}>
                  <Link to={`/app/sessions/${s.id}`} className="flex items-center justify-between gap-3 group">
                    <span className="text-sm text-ink-200 group-hover:text-ink-100 truncate">
                      {s.title ?? `${s.source_tool} session`}
                    </span>
                    <span className="flex gap-2 shrink-0">
                      <Badge label={s.source_fidelity} />
                      <Badge label={s.extraction_status} />
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display font-semibold text-ink-100">Mastery breakdown</h2>
            <Link to="/app/profile" className="text-xs text-primary-300 hover:text-primary-400">
              Full profile →
            </Link>
          </div>
          {profile.entries.length === 0 ? (
            <p className="text-sm text-ink-300">Your Knowledge Profile builds itself from demonstrated recall — complete reviews to grow it.</p>
          ) : (
            <div className="space-y-2.5">
              {(['consolidated', 'learning', 'new', 'stale'] as const).map((status) => {
                const count = counts[status] ?? 0
                const pct = profile.entries.length ? Math.round((count / profile.entries.length) * 100) : 0
                const bar = { consolidated: 'bg-good-500', learning: 'bg-primary-500', new: 'bg-ink-600', stale: 'bg-warn-500' }[status]
                return (
                  <div key={status} className="flex items-center gap-3 text-sm">
                    <span className="w-28 text-ink-300 capitalize">{status}</span>
                    <div className="flex-1 h-2 rounded-full bg-ink-800 overflow-hidden">
                      <div className={`h-full rounded-full ${bar}`} style={{ width: `${pct}%` }} />
                    </div>
                    <span className="w-8 text-right text-ink-200">{count}</span>
                  </div>
                )
              })}
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
