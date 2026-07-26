import { useMemo, useState } from 'react'
import type { Artifact } from '../lib/types'
import Markdown from './Markdown'
import Mermaid from './Mermaid'
import { Badge, Button, TextArea } from './ui'

type Performance = 'correct' | 'partial' | 'incorrect'

interface PlayerProps {
  artifact: Artifact
  mode: 'learn' | 'review'
  onGrade?: (performance: Performance, responseText: string) => void
  grading?: boolean
}

function GradeButtons({
  onGrade,
  grading,
  responseText,
}: {
  onGrade: (p: Performance, r: string) => void
  grading?: boolean
  responseText: string
}) {
  return (
    <div>
      <p className="text-sm text-ink-300 mb-2">How was your recall — honestly?</p>
      <div className="flex flex-wrap gap-2">
        <Button
          disabled={grading}
          onClick={() => onGrade('correct', responseText)}
          className="!bg-good-500/15 !text-good-500 border border-good-500/40 !shadow-none hover:!bg-good-500/25"
        >
          Got it
        </Button>
        <Button
          disabled={grading}
          onClick={() => onGrade('partial', responseText)}
          className="!bg-warn-500/15 !text-warn-500 border border-warn-500/40 !shadow-none hover:!bg-warn-500/25"
        >
          Partially
        </Button>
        <Button
          disabled={grading}
          onClick={() => onGrade('incorrect', responseText)}
          className="!bg-bad-500/15 !text-bad-500 border border-bad-500/40 !shadow-none hover:!bg-bad-500/25"
        >
          Didn't recall
        </Button>
      </div>
    </div>
  )
}

const LEARN_FOOTNOTE = (
  <p className="text-xs text-ink-300">
    This was practice, not a graded review — only graded recall in review sessions updates your mastery.
  </p>
)

/** Flashcards: flip to reveal — no forced typing. */
function FlashcardPlayer({ artifact, mode, onGrade, grading }: PlayerProps) {
  const cards = artifact.content.cards ?? []
  const [index, setIndex] = useState(0)
  const [flipped, setFlipped] = useState(false)
  const card = cards[index]
  if (!card) return null
  const isLast = index === cards.length - 1

  return (
    <div className="space-y-4">
      <button
        onClick={() => setFlipped((f) => !f)}
        className={`w-full text-left rounded-xl border p-5 min-h-28 transition-colors cursor-pointer ${
          flipped ? 'border-primary-600/60 bg-primary-600/10' : 'border-ink-600 bg-ink-800 hover:border-primary-600/40'
        }`}
        title="Click to flip"
      >
        <p className="text-[10px] uppercase tracking-widest text-ink-300 mb-2">
          {flipped ? 'Back' : 'Front — recall it, then flip'}
        </p>
        <Markdown>{flipped ? card.back : card.front}</Markdown>
      </button>
      <div className="flex items-center justify-between gap-3">
        <Button variant="secondary" onClick={() => setFlipped((f) => !f)}>
          {flipped ? 'Show front' : 'Flip card'}
        </Button>
        {cards.length > 1 && (
          <span className="text-xs text-ink-300">
            {index + 1} / {cards.length}
          </span>
        )}
        {!isLast && (
          <Button
            variant="secondary"
            onClick={() => {
              setIndex(index + 1)
              setFlipped(false)
            }}
          >
            Next card →
          </Button>
        )}
      </div>
      {isLast && flipped && mode === 'review' && onGrade && (
        <GradeButtons onGrade={onGrade} grading={grading} responseText="(flashcard session)" />
      )}
      {isLast && flipped && mode === 'learn' && LEARN_FOOTNOTE}
    </div>
  )
}

/** MCQ: pick an answer, get instant feedback; review mode auto-computes the grade. */
function McqPlayer({ artifact, mode, onGrade, grading }: PlayerProps) {
  const questions = artifact.content.questions ?? []
  const [index, setIndex] = useState(0)
  const [picked, setPicked] = useState<number | null>(null)
  const [results, setResults] = useState<boolean[]>([])
  const q = questions[index]
  if (!q || !q.choices) return null
  const isLast = index === questions.length - 1
  const answered = picked !== null
  const finished = isLast && answered

  const pick = (i: number) => {
    if (answered) return
    setPicked(i)
    setResults((r) => [...r, i === q.correct_index])
  }

  const next = () => {
    setIndex(index + 1)
    setPicked(null)
  }

  const correctCount = results.filter(Boolean).length
  const finalGrade: Performance =
    correctCount === questions.length ? 'correct' : correctCount > 0 ? 'partial' : 'incorrect'

  return (
    <div className="space-y-4">
      {questions.length > 1 && (
        <p className="text-xs text-ink-300">
          Question {index + 1} / {questions.length}
        </p>
      )}
      <Markdown>{q.question}</Markdown>
      <div className="space-y-2">
        {q.choices.map((choice, i) => {
          let style = 'border-ink-600 bg-ink-800 hover:border-primary-600/50'
          if (answered) {
            if (i === q.correct_index) style = 'border-good-500/60 bg-good-500/10'
            else if (i === picked) style = 'border-bad-500/60 bg-bad-500/10'
            else style = 'border-ink-700 bg-ink-900 opacity-60'
          }
          return (
            <button
              key={i}
              onClick={() => pick(i)}
              disabled={answered}
              className={`w-full text-left rounded-lg border px-4 py-2.5 text-sm text-ink-100 transition-colors ${style}`}
            >
              <span className="text-ink-300 mr-2">{String.fromCharCode(65 + i)}.</span>
              {choice}
            </button>
          )
        })}
      </div>
      {answered && (
        <div className="fade-up space-y-3">
          <p className={`text-sm font-medium ${picked === q.correct_index ? 'text-good-500' : 'text-bad-500'}`}>
            {picked === q.correct_index ? 'Correct.' : `Not quite — ${String.fromCharCode(65 + (q.correct_index ?? 0))} is right.`}
          </p>
          {q.explanation && (
            <div className="rounded-lg border border-ink-600 bg-ink-800 p-3 text-sm text-ink-200">{q.explanation}</div>
          )}
          {!isLast && (
            <Button variant="secondary" onClick={next}>
              Next question →
            </Button>
          )}
        </div>
      )}
      {finished && mode === 'review' && onGrade && (
        <div className="fade-up">
          <p className="text-sm text-ink-300 mb-2">
            Score: {correctCount}/{questions.length} — recorded as “{finalGrade}”.
          </p>
          <Button
            disabled={grading}
            onClick={() => onGrade(finalGrade, `MCQ score ${correctCount}/${questions.length}`)}
          >
            Finish review
          </Button>
        </div>
      )}
      {finished && mode === 'learn' && LEARN_FOOTNOTE}
    </div>
  )
}

/** Diagram: shown immediately with its explanation. */
function DiagramPlayer({ artifact, mode, onGrade, grading }: PlayerProps) {
  const c = artifact.content
  return (
    <div className="space-y-4">
      <div className="card p-4">{c.mermaid && <Mermaid chart={c.mermaid} />}</div>
      {c.explanation && <Markdown>{c.explanation}</Markdown>}
      {mode === 'review' && onGrade && (
        <div className="space-y-3">
          {c.recall_prompt && <p className="text-sm text-ink-300">{c.recall_prompt}</p>}
          <GradeButtons onGrade={onGrade} grading={grading} responseText="(diagram review)" />
        </div>
      )}
    </div>
  )
}

/** Open-recall formats: attempt first, then reveal (testing effect). */
function RecallPlayer({ artifact, mode, onGrade, grading }: PlayerProps) {
  const items = useMemo(() => {
    const c = artifact.content
    switch (c.type) {
      case 'qa':
        return (c.questions ?? []).map((q) => ({
          prompt: q.question,
          answer: null as string | null,
          expectedPoints: q.expected_points,
        }))
      case 'retrieval_practice':
        return (c.questions ?? []).map((q) => ({ prompt: q.question, answer: q.answer ?? null, expectedPoints: undefined }))
      case 'self_explanation':
        return (c.prompts ?? []).map((p) => ({ prompt: p.prompt, answer: p.context || null, expectedPoints: undefined }))
      case 'synthesis':
        return [
          {
            prompt: c.prompt ?? 'Synthesize what you learned.',
            answer: (c.related_titles ?? []).join(', ') || null,
            expectedPoints: undefined,
          },
        ]
      default:
        return [{ prompt: 'Recall what you learned in this span.', answer: null, expectedPoints: undefined }]
    }
  }, [artifact])
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
      {items.length > 1 && (
        <p className="text-xs text-ink-300">
          {index + 1} / {items.length}
        </p>
      )}
      <Markdown>{item.prompt}</Markdown>
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
          {item.answer && (
            <div className="rounded-lg border border-ink-600 bg-ink-800 p-4">
              <Markdown>{item.answer}</Markdown>
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
            <GradeButtons onGrade={onGrade} grading={grading} responseText={[...attempts, attempt].join('\n---\n')} />
          )}
          {isLast && mode === 'learn' && LEARN_FOOTNOTE}
        </div>
      )}
    </div>
  )
}

/**
 * Artifact player. Recall formats gate reveal behind an attempt (testing effect);
 * flashcards flip, diagrams and MCQs are interactive. In review mode the grade —
 * and only the grade — updates mastery.
 */
export default function ArtifactPlayer(props: PlayerProps) {
  const type = props.artifact.content.type
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <Badge label={props.artifact.format} />
      </div>
      {type === 'flashcard' ? (
        <FlashcardPlayer {...props} />
      ) : type === 'mcq' ? (
        <McqPlayer {...props} />
      ) : type === 'diagram' ? (
        <DiagramPlayer {...props} />
      ) : (
        <RecallPlayer {...props} />
      )}
    </div>
  )
}
