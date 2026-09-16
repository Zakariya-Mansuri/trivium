import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import type { ReactNode } from 'react'
import { useAuth } from '../context/AuthContext'

/* ═══════════════════════════════════════════════════════════════════════
   App shell — Teletype
   research/v2/features/01-design-foundation.md

   · Nine flat nav items become FOUR DISTRICTS (Hick's Law; Lynch legibility,
     field guide §6.2). Every existing route stays reachable.
   · The glyph nav (◈ ⌨ ☰ ▣ ✦ ↻ ⬡ ∿) is gone. Those were font-dependent, so
     the nav rendered differently on every OS and could not be styled as a set.
   · Responsive: sidebar on md+, bottom rail below. The shipped layout had no
     breakpoint at all — a 224px sidebar took 60% of a 375px screen.
   ═══════════════════════════════════════════════════════════════════════ */

/* Icons: inline SVG, 16px, currentColor, 1.5 stroke. No icon font, no glyphs. */
const icon = (paths: ReactNode) => (
  <svg
    viewBox="0 0 24 24"
    width="16"
    height="16"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="square"
    strokeLinejoin="miter"
    aria-hidden="true"
    focusable="false"
  >
    {paths}
  </svg>
)

const Icons = {
  home: icon(<><path d="M4 4h6v6H4z" /><path d="M14 4h6v6h-6z" /><path d="M4 14h6v6H4z" /><path d="M14 14h6v6h-6z" /></>),
  inherit: icon(<><path d="M4 14v5h16v-5" /><path d="M12 4v9" /><path d="M8 9l4 4 4-4" /></>),
  work: icon(<><path d="M4 7l4 4-4 4" /><path d="M12 15h8" /></>),
  retain: icon(<><path d="M20 12a8 8 0 1 1-2.6-5.9" /><path d="M20 4v4h-4" /></>),
  contribute: icon(<><path d="M4 14v5h16v-5" /><path d="M12 15V4" /><path d="M8 8l4-4 4 4" /></>),
}

type Item = { to: string; label: string; end?: boolean }
type District = { key: string; label: string; icon: ReactNode; primary: string; items: Item[] }

const DISTRICTS: District[] = [
  {
    key: 'inherit',
    label: 'Inherit',
    icon: Icons.inherit,
    primary: '/app/sessions',
    items: [
      { to: '/app/sessions', label: 'Sessions' },
      { to: '/app/projects', label: 'Projects' },
    ],
  },
  {
    key: 'work',
    label: 'Work',
    icon: Icons.work,
    primary: '/app/agent',
    items: [{ to: '/app/agent', label: 'Agent' }],
  },
  {
    key: 'retain',
    label: 'Retain',
    icon: Icons.retain,
    primary: '/app/review',
    items: [
      { to: '/app/review', label: 'Review' },
      { to: '/app/learn', label: 'Learn' },
      { to: '/app/profile', label: 'Profile' },
      { to: '/app/metrics', label: 'Metrics' },
    ],
  },
  {
    key: 'contribute',
    label: 'Contribute',
    icon: Icons.contribute,
    primary: '/app/skills',
    items: [{ to: '/app/skills', label: 'Skills' }],
  },
]

const subLink =
  'block px-3 py-2 text-[13px] transition-colors motion-micro border-l border-rule -ml-px'
const subActive = 'text-ink border-ribbon font-medium'
const subIdle = 'text-ink-lo hover:text-ink hover:border-edge'

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <div className="min-h-screen md:flex">
      {/* ── sidebar (md and up) ───────────────────────────────────────── */}
      <aside className="hidden md:flex w-56 shrink-0 border-r border-edge bg-surface flex-col sticky top-0 h-screen">
        <div className="px-4 py-4 border-b border-rule">
          <NavLink to="/" className="font-display text-base font-semibold text-ink lowercase tracking-tight">
            <span className="text-ribbon">▚</span> trivium
          </NavLink>
          <p className="text-[11px] text-ink-lo mt-1 leading-tight">
            everything you know, someone left for you
          </p>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-5 overflow-y-auto" aria-label="Districts">
          <NavLink
            to="/app"
            end
            className={({ isActive }) =>
              `flex items-center gap-2.5 px-2 py-2 text-[13px] transition-colors motion-micro ${
                isActive ? 'text-ink font-medium' : 'text-ink-lo hover:text-ink'
              }`
            }
          >
            {Icons.home}
            Dashboard
          </NavLink>

          {DISTRICTS.map((d) => (
            <div key={d.key}>
              <p className="flex items-center gap-2.5 px-2 pb-2 text-[10px] uppercase tracking-[0.16em] text-ink-lo">
                <span className="text-ribbon">{d.icon}</span>
                {d.label}
              </p>
              <div className="pl-2 border-l border-rule ml-2">
                {d.items.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.end}
                    className={({ isActive }) => `${subLink} ${isActive ? subActive : subIdle}`}
                  >
                    {item.label}
                  </NavLink>
                ))}
              </div>
            </div>
          ))}
        </nav>

        <div className="border-t border-rule px-4 py-3">
          <p className="text-[13px] text-ink truncate">{user?.display_name ?? user?.email}</p>
          <div className="flex gap-3 mt-1.5 text-[11px]">
            <NavLink to="/app/settings" className="text-ink-lo hover:text-ink">
              Settings
            </NavLink>
            <button
              onClick={async () => {
                await logout()
                navigate('/')
              }}
              className="text-ink-lo hover:text-ribbon min-h-6"
            >
              Log out
            </button>
          </div>
        </div>
      </aside>

      {/* ── mobile header ─────────────────────────────────────────────── */}
      <header className="md:hidden flex items-center justify-between gap-3 border-b border-edge bg-surface px-4 py-3 sticky top-0 z-20">
        <NavLink to="/" className="font-display text-base font-semibold text-ink lowercase tracking-tight">
          <span className="text-ribbon">▚</span> trivium
        </NavLink>
        <div className="flex items-center gap-3 text-[11px]">
          <NavLink to="/app/settings" className="text-ink-lo min-h-11 flex items-center px-1">
            Settings
          </NavLink>
          <button
            onClick={async () => {
              await logout()
              navigate('/')
            }}
            className="text-ink-lo min-h-11 px-1"
          >
            Log out
          </button>
        </div>
      </header>

      {/* ── content ───────────────────────────────────────────────────── */}
      <main className="flex-1 min-w-0 px-5 py-6 md:px-10 md:py-8 pb-24 md:pb-8 max-w-5xl mx-auto w-full">
        <Outlet />
      </main>

      {/* ── bottom rail (below md) — 44px+ targets, SC 2.5.8 ──────────── */}
      <nav
        className="md:hidden fixed bottom-0 inset-x-0 z-30 grid grid-cols-5 border-t border-edge bg-surface"
        aria-label="Districts"
      >
        <NavLink
          to="/app"
          end
          className={({ isActive }) =>
            `flex flex-col items-center justify-center gap-1 min-h-14 py-2 text-[10px] uppercase tracking-[0.1em] ${
              isActive ? 'text-ribbon' : 'text-ink-lo'
            }`
          }
        >
          {Icons.home}
          Home
        </NavLink>
        {DISTRICTS.map((d) => (
          <NavLink
            key={d.key}
            to={d.primary}
            className={({ isActive }) =>
              `flex flex-col items-center justify-center gap-1 min-h-14 py-2 text-[10px] uppercase tracking-[0.1em] ${
                isActive ? 'text-ribbon' : 'text-ink-lo'
              }`
            }
          >
            {d.icon}
            {d.label}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
