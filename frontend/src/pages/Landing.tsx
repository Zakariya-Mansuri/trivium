import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const science = [
  { principle: 'Testing effect', source: 'Roediger & Karpicke', how: 'Every quiz defaults to open recall — never multiple choice.' },
  { principle: 'Spacing', source: 'Ebbinghaus · Bjork · Cepeda', how: 'Adaptive intervals per concept, tuned by your performance.' },
  { principle: 'Interleaving', source: 'Oakley · Dunlosky', how: 'Review sessions deliberately mix concepts across projects.' },
  { principle: 'Diffuse mode', source: 'Oakley', how: 'First review is intentionally delayed — no cramming right after coding.' },
  { principle: 'Desirable difficulty', source: 'Bjork', how: 'Friction that aids retention stays. We say why, instead of smoothing it away.' },
  { principle: 'No illusions of competence', source: 'Oakley', how: 'Passively viewing answers never counts. Only demonstrated recall updates mastery.' },
]

const loop = [
  { step: '1', title: 'Code with AI', text: 'Use the built-in agent or paste sessions from Claude Code, Cursor, Copilot.' },
  { step: '2', title: 'Knowledge extracted', text: 'Concepts, decisions, bug-fixes and patterns are tagged into your longitudinal knowledge graph.' },
  { step: '3', title: 'Learn on demand', text: 'Hit Learn on a message, a chat, a project, or a whole month. Recall-first artifacts, auto-formatted.' },
  { step: '4', title: 'Reviews that stick', text: 'Spaced, interleaved reviews and an evidence-based Knowledge Profile that proves you\'re getting sharper.' },
]

export default function Landing() {
  const { user } = useAuth()
  return (
    <div className="min-h-screen bg-ink-950">
      <header className="max-w-5xl mx-auto flex items-center justify-between px-6 py-5">
        <span className="font-display text-lg font-bold">
          <span className="text-primary-400">▲</span> Trivium
        </span>
        <nav className="flex items-center gap-4 text-sm">
          {user ? (
            <Link to="/app" className="rounded-lg bg-primary-600 hover:bg-primary-500 px-4 py-2 font-medium text-white">
              Open app
            </Link>
          ) : (
            <>
              <Link to="/login" className="text-ink-200 hover:text-ink-100">
                Log in
              </Link>
              <Link to="/signup" className="rounded-lg bg-primary-600 hover:bg-primary-500 px-4 py-2 font-medium text-white">
                Get started
              </Link>
            </>
          )}
        </nav>
      </header>

      <section className="max-w-5xl mx-auto px-6 pt-20 pb-16 text-center">
        <p className="text-xs uppercase tracking-[0.25em] text-accent-400 mb-5">The learning layer for AI-assisted coding</p>
        <h1 className="font-display text-4xl md:text-6xl font-bold leading-tight text-ink-100">
          Vibe code without
          <br />
          <span className="text-primary-400">getting dumber.</span>
        </h1>
        <p className="text-ink-300 mt-6 max-w-2xl mx-auto leading-relaxed">
          AI coding tools optimize for shipping speed. Trivium adds the missing layer: it turns your chats, diffs,
          decisions and bug-fixes into durable knowledge — so six months from now you can still explain, rebuild,
          and extend what you shipped.
        </p>
        <div className="mt-9 flex justify-center gap-4">
          <Link to="/signup" className="rounded-lg bg-primary-600 hover:bg-primary-500 px-6 py-3 font-medium text-white shadow-lg shadow-primary-600/25">
            Start learning from your code
          </Link>
          <a href="#science" className="rounded-lg border border-ink-600 px-6 py-3 font-medium text-ink-200 hover:bg-ink-800">
            The science
          </a>
        </div>
        <p className="text-xs text-ink-300 mt-5">Coding correctness is table stakes — we measure whether you got smarter.</p>
      </section>

      <section className="max-w-5xl mx-auto px-6 py-14">
        <div className="grid md:grid-cols-4 gap-4">
          {loop.map((item) => (
            <div key={item.step} className="card p-5">
              <span className="text-primary-400 font-display text-sm font-bold">{item.step}</span>
              <h3 className="font-display font-semibold text-ink-100 mt-2">{item.title}</h3>
              <p className="text-sm text-ink-300 mt-2 leading-relaxed">{item.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="science" className="max-w-5xl mx-auto px-6 py-14">
        <h2 className="font-display text-2xl font-semibold text-center text-ink-100">
          Every mechanic traces to real research
        </h2>
        <p className="text-ink-300 text-sm text-center mt-2 mb-8 max-w-xl mx-auto">
          Not gamification. Not streaks. The review engine is constrained by established learning science — even when
          that means deliberate friction.
        </p>
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-ink-300 border-b border-ink-700">
                <th className="px-5 py-3 font-medium">Principle</th>
                <th className="px-5 py-3 font-medium">Research</th>
                <th className="px-5 py-3 font-medium">In Trivium</th>
              </tr>
            </thead>
            <tbody>
              {science.map((row) => (
                <tr key={row.principle} className="border-b border-ink-800 last:border-0">
                  <td className="px-5 py-3.5 text-ink-100 font-medium whitespace-nowrap">{row.principle}</td>
                  <td className="px-5 py-3.5 text-ink-300 whitespace-nowrap">{row.source}</td>
                  <td className="px-5 py-3.5 text-ink-200">{row.how}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="max-w-3xl mx-auto px-6 py-20 text-center">
        <h2 className="font-display text-3xl font-semibold text-ink-100">
          Your future self will ask what you actually learned.
        </h2>
        <p className="text-ink-300 mt-4">Have an evidence-backed answer.</p>
        <Link
          to="/signup"
          className="inline-block mt-8 rounded-lg bg-primary-600 hover:bg-primary-500 px-8 py-3 font-medium text-white shadow-lg shadow-primary-600/25"
        >
          Create your Knowledge Profile
        </Link>
      </section>

      <footer className="border-t border-ink-800 py-8 text-center text-xs text-ink-300">
        Trivium — retrieval over exposure, evidence over self-report.
      </footer>
    </div>
  )
}
