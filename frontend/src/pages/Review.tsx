import { useCallback, useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import ArtifactPlayer from '../components/ArtifactPlayer'
import { Badge, Button, Card, EmptyState, ErrorNote, PageHeader, Spinner } from '../components/ui'
import { api } from '../lib/api'
import type { ReviewQueue, ReviewResult } from '../lib/types'

export default function Review() {
  const [params, setParams] = useSearchParams()
  const earlyMode = params.get('early') === '1'
  const [queue, setQueue] = useState<ReviewQueue | null>(null)
  const [index, setIndex] = useState(0)
  const [lastResult, setLastResult] = useState<ReviewResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [done, setDone] = useState(0)

  const load = useCallback(async () => {
    setQueue(await api<ReviewQueue>(`/reviews/queue${earlyMode ? '?early=true' : ''}`))
    setIndex(0)
  }, [earlyMode])

  useEffect(() => {
    load().catch((e) => setError(e.message))
  }, [load])

  if (error && !queue) return <p className="text-bad-500">{error}</p>
  if (!queue) return <Spinner label="Building your interleaved session…" />

  const item = queue.items[index]

  const grade = async (performance: 'correct' | 'partial' | 'incorrect', responseText: string) => {
    if (!item) return
    setBusy(true)
    setError(null)
    try {
      const result = await api<ReviewResult>('/reviews/submit', {
        method: 'POST',
        body: {
          unit_id: item.unit.id,
          artifact_id: item.artifact.id,
          performance,
          response_text: responseText,
          early: item.early,
        },
      })
      setLastResult(result)
      setDone((d) => d + 1)
      if (index + 1 < queue.items.length) {
        setIndex(index + 1)
      } else {
        await load()
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Submit failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="fade-up max-w-3xl">
      <PageHeader
        title="Review"
        subtitle={
          queue.items.length > 0
            ? `${queue.total_due} due · mixed across ${Math.max(queue.projects_in_session, 1)} project${queue.projects_in_session === 1 ? '' : 's'} — interleaving is deliberate, it strengthens discrimination between concepts.`
            : undefined
        }
        action={
          earlyMode ? (
            <Button variant="secondary" onClick={() => setParams({})}>
              Back to due-only
            </Button>
          ) : undefined
        }
      />

      {lastResult && (
        <Card className="mb-5 !py-3 border-good-500/30">
          <p className="text-xs text-ink-300">
            Scheduled next: <span className="text-ink-100">{new Date(lastResult.next_review_at).toLocaleString()}</span>
            {' · '}interval {lastResult.interval_days}d · status <Badge label={lastResult.mastery_status} />
          </p>
        </Card>
      )}

      <ErrorNote message={error} />

      {queue.items.length === 0 ? (
        <EmptyState
          title={done > 0 ? `Queue cleared — ${done} review${done === 1 ? '' : 's'} done 🎉` : 'Nothing due for review'}
          hint={
            queue.next_due_at
              ? `Next review unlocks ${new Date(queue.next_due_at).toLocaleString()}. Spacing out recall is what makes it stick — but reviewing early is your call.`
              : 'Trigger Learn on a session to start tracking concepts.'
          }
          action={
            queue.total_early > 0 ? (
              <Button onClick={() => setParams({ early: '1' })}>
                Review {Math.min(queue.total_early, 10)} upcoming item{queue.total_early === 1 ? '' : 's'} early
              </Button>
            ) : (
              <Link to="/app/learn" className="text-primary-300 hover:text-primary-400 text-sm">
                Go to Learn →
              </Link>
            )
          }
        />
      ) : (
        item && (
          <Card>
            <div className="flex items-center justify-between gap-3 mb-4">
              <div className="min-w-0">
                <p className="text-xs text-ink-300 mb-1">
                  {index + 1} of {queue.items.length} · {item.unit.unit_type.replace(/_/g, ' ')}
                  {item.early && <span className="text-accent-400"> · early — spacing works better, but it's your call</span>}
                </p>
                <h2 className="font-display font-semibold text-ink-100 truncate">{item.unit.title}</h2>
              </div>
              <Badge label={item.mastery_status} />
            </div>
            <ArtifactPlayer key={item.unit.id} artifact={item.artifact} mode="review" onGrade={grade} grading={busy} />
          </Card>
        )
      )}
    </div>
  )
}
