import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const nav = [
  { to: '/app', label: 'Dashboard', icon: '◈', end: true },
  { to: '/app/agent', label: 'Agent', icon: '⌨' },
  { to: '/app/sessions', label: 'Sessions', icon: '☰' },
  { to: '/app/projects', label: 'Projects', icon: '▣' },
  { to: '/app/learn', label: 'Learn', icon: '✦' },
  { to: '/app/review', label: 'Review', icon: '↻' },
  { to: '/app/profile', label: 'Profile', icon: '⬡' },
  { to: '/app/skills', label: 'Improve', icon: '↑' },
  { to: '/app/metrics', label: 'Metrics', icon: '∿' },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <div className="flex min-h-screen">
      <aside className="w-56 shrink-0 border-r border-ink-700 bg-ink-900 flex flex-col sticky top-0 h-screen">
        <div className="px-5 py-5 border-b border-ink-700">
          <NavLink to="/" className="font-display text-lg font-bold text-ink-100">
            <span className="text-primary-400">▲</span> Trivium
          </NavLink>
          <p className="text-[11px] text-ink-300 mt-1 leading-tight">Vibe code without getting dumber</p>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                  isActive
                    ? 'bg-primary-600/15 text-primary-300 font-medium'
                    : 'text-ink-200 hover:bg-ink-800 hover:text-ink-100'
                }`
              }
            >
              <span className="text-base w-4 text-center">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-ink-700 px-4 py-4">
          <p className="text-sm text-ink-100 truncate">{user?.display_name ?? user?.email}</p>
          <div className="flex gap-3 mt-2 text-xs">
            <NavLink to="/app/settings" className="text-ink-300 hover:text-ink-100">
              Settings
            </NavLink>
            <button
              onClick={async () => {
                await logout()
                navigate('/')
              }}
              className="text-ink-300 hover:text-bad-500"
            >
              Log out
            </button>
          </div>
        </div>
      </aside>
      <main className="flex-1 min-w-0 px-6 py-8 lg:px-10 max-w-6xl">
        <Outlet />
      </main>
    </div>
  )
}
