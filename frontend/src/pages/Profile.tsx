import { useEffect, useState } from 'react'
import { Badge, Button, Card, EmptyState, ErrorNote, PageHeader, Spinner } from '../components/ui'
import { api } from '../lib/api'
import type { Profile as ProfileType, ProfileEntry } from '../lib/types'

const trendGlyph = { improving: '↗', stable: '→', declining: '↘' } as const

export default function Profile() {
  const [profile, setProfile] = useState<ProfileType | null>(null)
  const [filter, setFilter] = useState<string>('all')
  const [error, setError] = useState<string | null>(null)

  const load = () => api<ProfileType>('/profile').then(setProfile).catch((e) => setError(e.message))
  useEffect(() => {
    load()
  }, [])

  const toggleVisibility = async (entry: ProfileEntry) => {
    try {
      await api(`/profile/entries/${entry.entry_id}/visibility`, {
        method: 'PATCH',
        body: { visibility: entry.visibility === 'private' ? 'shared' : 'private' },
      })
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update visibility')
    }
  }

  const download = async (audience: 'private' | 'shared') => {
    try {
      const md = await api<string>(`/profile/export?audience=${audience}`, { raw: true })
      const blob = new Blob([md], { type: 'text/markdown' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'skill.md'
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed')
    }
  }

  if (error && !profile) return <p className="text-bad-500">{error}</p>
  if (!profile) return <Spinner label="Computing your evidence-based profile…" />

  const statuses = ['all', 'consolidated', 'learning', 'new', 'stale']
  const entries = filter === 'all' ? profile.entries : profile.entries.filter((e) => e.mastery_status === filter)

  return (
    <div className="fade-up">
      <PageHeader
        title="Knowledge Profile"
        subtitle="Your skill.md — every status is earned by demonstrated recall, never self-reported. Private by default; share entries individually."
        action={
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => download('shared')}>
              Export shared only
            </Button>
            <Button onClick={() => download('private')}>Export skill.md</Button>
          </div>
        }
      />

      <ErrorNote message={error} />

      <div className="flex flex-wrap gap-2 mb-6">
        {statuses.map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`rounded-full border px-3.5 py-1.5 text-xs font-medium capitalize transition-colors ${
              filter === s ? 'border-primary-500 bg-primary-600/15 text-primary-300' : 'border-ink-600 text-ink-300 hover:text-ink-100'
            }`}
          >
            {s} {s !== 'all' && `(${profile.counts[s] ?? 0})`}
          </button>
        ))}
      </div>

      {entries.length === 0 ? (
        <EmptyState
          title="No evidence yet"
          hint="Complete spaced reviews to build your profile — mastery only moves when you demonstrate recall."
        />
      ) : (
        <div className="space-y-3">
          {entries.map((e) => (
            <Card key={e.entry_id} className="!py-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="text-ink-100 font-medium truncate">{e.unit.title}</p>
                    {e.retention_trend && (
                      <span
                        title={`Retention ${e.retention_trend}`}
                        className={
                          e.retention_trend === 'improving'
                            ? 'text-good-500'
                            : e.retention_trend === 'declining'
                              ? 'text-warn-500'
                              : 'text-ink-300'
                        }
                      >
                        {trendGlyph[e.retention_trend]}
                      </span>
                    )}
                  </div>
                  {e.unit.summary && <p className="text-xs text-ink-300 mt-1 line-clamp-2">{e.unit.summary}</p>}
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <Badge label={e.unit.unit_type} />
                  <Badge label={e.mastery_status} />
                  <button
                    onClick={() => toggleVisibility(e)}
                    className={`rounded-full border px-2.5 py-0.5 text-xs transition-colors ${
                      e.visibility === 'shared'
                        ? 'border-accent-500/40 bg-accent-500/15 text-accent-400'
                        : 'border-ink-600 text-ink-300 hover:text-ink-100'
                    }`}
                    title="Toggle whether this entry appears in shared exports"
                  >
                    {e.visibility}
                  </button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
