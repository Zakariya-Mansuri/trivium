import { useMemo, useState } from 'react'
import type { Artifact } from '../lib/types'
import Mermaid from './Mermaid'
import { Badge, Button, TextArea } from './ui'

interface Item {
  prompt: string
  answer: string | null
  expectedPoints?: string[]
  mermaid?: string
}

function itemsFromArtifact(artifact: Artifact): Item[] {
  const c = artifact.content
  switch (c.type) {
    case 'flashcard':
      return (c.cards ?? []).map((card) => ({ prompt: card.front, answer: card.back }))
    case 'qa':
      return (c.questions ?? []).map((q) => ({
        prompt: q.question,
        answer: null,
        expectedPoints: q.expected_points,
      }))
    case 'retrieval_practice':
      return (c.questions ?? []).map((q) => ({ prompt: q.question, answer: q.answer ?? null }))
    case 'self_explanation':
      return (c.prompts ?? []).map((p) => ({ prompt: p.prompt, answer: p.context || null }))
    case 'synthesis':
      return [{ prompt: c.prompt ?? 'Synthesize what you learned.', answer: (c.related_titles ?? []).join(', ') || null }]
    case 'diagram':
      return [
        {
          prompt: c.recall_prompt ?? 'From memory: how do these components connect?',
          answer: c.explanation ?? null,
          mermaid: c.mermaid,
        },
      ]
    default:
      return [{ prompt: 'Recall what you learned in this span.', answer: null }]
  }
}

/**
 * Active-recall player: the user must attempt before revealing (testing effect).
 * In review mode a self-grade is required after reveal; the grade is the only
 * thing that ever updates mastery — never the viewing itself.
 */
export default function ArtifactPlayer({
  artifact,
  mode,
  onGrade,
  grading,
}: {
  artifact: Artifact
  mode: 'learn' | 'review'
  onGrade?: (performance: 'correct' | 'partial' | 'incorrect', responseText: string) => void
  grading?: boolean
}) {
  const items = useMemo(() => itemsFromArtifact(artifact), [artifact])
  const [index, setIndex] = useState(0)
  const [attempt, setAttempt] = useState('')
  const [revealed, setRevealed] = useState(false)
  const [attempts, setAttempts] = useState<string[]>([])

  const item = items[index]
  if (!item) return null
  const isLast = index === items.length - 1

  const next = () => {
    setAttempts((prev) => [...prev, attempt])
    setIndex((i) => i + 1)
    setAttempt('')
    setRevealed(false)
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <Badge label={artifact.format} />
        {items.length > 1 && (
          <span className="text-xs text-ink-300">
            {index + 1} / {items.length}
          </span>
        )}
      </div>

      <p className="text-ink-100 leading-relaxed">{item.prompt}</p>

      <TextArea
        rows={4}
        placeholder="Answer from memory first — that's the whole point. Recall beats re-reading."
        value={attempt}
        onChange={(e) => setAttempt(e.target.value)}
        disabled={revealed && mode === 'review'}
      />

      {!revealed ? (
        <Button variant="secondary" onClick={() => setRevealed(true)} disabled={attempt.trim().length === 0}>
          {attempt.trim().length === 0 ? 'Write your attempt first' : 'Reveal'}
        </Button>
      ) : (
        <div className="space-y-4 fade-up">
          {item.mermaid && (
            <div className="card p-4">
              <Mermaid chart={item.mermaid} />
            </div>
          )}
          {item.answer && (
            <div className="rounded-lg border border-ink-600 bg-ink-800 p-4 text-sm text-ink-200 whitespace-pre-wrap">
              {item.answer}
            </div>
          )}
          {item.expectedPoints && item.expectedPoints.length > 0 && (
            <ul className="rounded-lg border border-ink-600 bg-ink-800 p-4 text-sm text-ink-200 list-disc list-inside space-y-1">
              {item.expectedPoints.map((p) => (
                <li key={p}>{p}</li>
              ))}
            </ul>
          )}

          {!isLast && (
            <Button variant="secondary" onClick={next}>
              Next prompt →
            </Button>
          )}

          {isLast && mode === 'review' && onGrade && (
            <div>
              <p className="text-sm text-ink-300 mb-2">How was your recall — honestly?</p>
              <div className="flex flex-wrap gap-2">
                <Button
                  disabled={grading}
                  onClick={() => onGrade('correct', [...attempts, attempt].join('\n---\n'))}
                  className="!bg-good-500/15 !text-good-500 border border-good-500/40 !shadow-none hover:!bg-good-500/25"
                >
                  Got it
                </Button>
                <Button
                  disabled={grading}
                  onClick={() => onGrade('partial', [...attempts, attempt].join('\n---\n'))}
                  className="!bg-warn-500/15 !text-warn-500 border border-warn-500/40 !shadow-none hover:!bg-warn-500/25"
                >
                  Partially
                </Button>
                <Button
                  disabled={grading}
                  onClick={() => onGrade('incorrect', [...attempts, attempt].join('\n---\n'))}
                  className="!bg-bad-500/15 !text-bad-500 border border-bad-500/40 !shadow-none hover:!bg-bad-500/25"
                >
                  Didn't recall
                </Button>
              </div>
            </div>
          )}

          {isLast && mode === 'learn' && (
            <p className="text-xs text-ink-300">
              This was practice, not a graded review — spaced reviews unlock after the consolidation window,
              and only graded recall updates your mastery.
            </p>
          )}
        </div>
      )}
    </div>
  )
}
