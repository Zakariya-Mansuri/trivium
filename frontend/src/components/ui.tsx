import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode, TextareaHTMLAttributes } from 'react'

export function Button({
  variant = 'primary',
  className = '',
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'ghost' | 'danger' }) {
  const styles = {
    primary:
      'bg-primary-600 hover:bg-primary-500 text-white shadow-lg shadow-primary-600/20 disabled:bg-ink-700 disabled:text-ink-300',
    secondary: 'bg-ink-800 hover:bg-ink-700 text-ink-100 border border-ink-600',
    ghost: 'bg-transparent hover:bg-ink-800 text-ink-200',
    danger: 'bg-bad-500/10 hover:bg-bad-500/20 text-bad-500 border border-bad-500/40',
  }[variant]
  return (
    <button
      className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors disabled:cursor-not-allowed ${styles} ${className}`}
      {...props}
    />
  )
}

export function Input({ className = '', ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={`w-full rounded-lg bg-ink-800 border border-ink-600 px-3 py-2 text-sm text-ink-100 placeholder-ink-300 outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 ${className}`}
      {...props}
    />
  )
}

export function TextArea({ className = '', ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={`w-full rounded-lg bg-ink-800 border border-ink-600 px-3 py-2 text-sm text-ink-100 placeholder-ink-300 outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 ${className}`}
      {...props}
    />
  )
}

export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`card p-5 ${className}`}>{children}</div>
}

const badgeColors: Record<string, string> = {
  concept: 'bg-primary-600/15 text-primary-300 border-primary-600/40',
  decision: 'bg-accent-500/15 text-accent-400 border-accent-500/40',
  bug_fix: 'bg-bad-500/15 text-bad-500 border-bad-500/40',
  pattern: 'bg-good-500/15 text-good-500 border-good-500/40',
  new: 'bg-ink-700 text-ink-200 border-ink-600',
  learning: 'bg-primary-600/15 text-primary-300 border-primary-600/40',
  consolidated: 'bg-good-500/15 text-good-500 border-good-500/40',
  stale: 'bg-warn-500/15 text-warn-500 border-warn-500/40',
  native: 'bg-good-500/15 text-good-500 border-good-500/40',
  wrapped: 'bg-warn-500/15 text-warn-500 border-warn-500/40',
  completed: 'bg-good-500/15 text-good-500 border-good-500/40',
  pending: 'bg-ink-700 text-ink-200 border-ink-600',
  running: 'bg-primary-600/15 text-primary-300 border-primary-600/40',
  failed: 'bg-bad-500/15 text-bad-500 border-bad-500/40',
  insufficient_content: 'bg-warn-500/15 text-warn-500 border-warn-500/40',
}

export function Badge({ label, className = '' }: { label: string; className?: string }) {
  const color = badgeColors[label] ?? 'bg-ink-700 text-ink-200 border-ink-600'
  return (
    <span className={`inline-block rounded-full border px-2.5 py-0.5 text-xs font-medium whitespace-nowrap ${color} ${className}`}>
      {label.replace(/_/g, ' ')}
    </span>
  )
}

export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 text-ink-300 text-sm py-8 justify-center">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-ink-600 border-t-primary-400" />
      {label ?? 'Loading…'}
    </div>
  )
}

export function EmptyState({ title, hint, action }: { title: string; hint?: string; action?: ReactNode }) {
  return (
    <div className="card p-10 text-center">
      <p className="text-ink-100 font-medium">{title}</p>
      {hint && <p className="text-ink-300 text-sm mt-2 max-w-md mx-auto">{hint}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  )
}

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: ReactNode }) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-4 mb-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink-100">{title}</h1>
        {subtitle && <p className="text-ink-300 text-sm mt-1 max-w-2xl">{subtitle}</p>}
      </div>
      {action}
    </div>
  )
}

export function ErrorNote({ message }: { message: string | null }) {
  if (!message) return null
  return (
    <div className="rounded-lg border border-bad-500/40 bg-bad-500/10 px-4 py-2.5 text-sm text-bad-500">
      {message}
    </div>
  )
}
