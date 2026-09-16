import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode, TextareaHTMLAttributes } from 'react'

/* ═══════════════════════════════════════════════════════════════════════
   UI kit — Teletype
   research/v2/features/01-design-foundation.md

   Rules enforced here:
   · SC 2.4.11 — every control carries a 2px ribbon :focus-visible ring.
   · SC 2.5.8  — every control is at least 44px tall.
   · Structural boundaries use --color-edge (3.12–3.50:1), never --color-rule.
   · Primary and danger are distinguished by WEIGHT, not hue: primary is a
     ribbon fill, danger is a ribbon outline. One accent, two actions.
   · No shadow anywhere except .prov-generated, which means "not yours yet".
   · No border radius. Enforced globally in index.css.
   ═══════════════════════════════════════════════════════════════════════ */

export function Button({
  variant = 'primary',
  className = '',
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'ghost' | 'danger' }) {
  const styles = {
    primary:
      'bg-ribbon text-paper border border-ribbon hover:bg-ribbon-deep hover:border-ribbon-deep ' +
      'disabled:bg-surface disabled:text-ink-lo disabled:border-edge',
    secondary: 'bg-transparent text-ink border border-edge hover:bg-ink hover:text-paper hover:border-ink',
    ghost: 'bg-transparent text-ink-mid border border-transparent hover:text-ink hover:border-edge',
    danger: 'bg-transparent text-ribbon border border-ribbon hover:bg-ribbon hover:text-paper',
  }[variant]
  return (
    <button
      className={
        `inline-flex items-center justify-center gap-2 min-h-11 px-4 py-2.5 text-[13px] ` +
        `font-medium uppercase tracking-[0.1em] transition-colors motion-micro ` +
        `disabled:cursor-not-allowed active:scale-[0.98] ${styles} ${className}`
      }
      {...props}
    />
  )
}

export function Input({ className = '', ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={
        `w-full min-h-11 bg-surface border border-edge px-3 py-2.5 text-sm text-ink ` +
        `placeholder-ink-lo outline-none focus:border-ribbon ${className}`
      }
      {...props}
    />
  )
}

export function TextArea({ className = '', ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={
        `w-full bg-surface border border-edge px-3 py-2.5 text-sm text-ink leading-relaxed ` +
        `placeholder-ink-lo outline-none focus:border-ribbon ${className}`
      }
      {...props}
    />
  )
}

export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`card p-5 ${className}`}>{children}</div>
}

/* Badges are square, not pills — a record, not a chat app. The colour is on
   the border and the text; nothing is filled, so nothing competes with the
   one ribbon fill on the primary action. */
const badgeColors: Record<string, string> = {
  concept: 'text-ink-mid border-edge',
  decision: 'text-ribbon border-ribbon',
  bug_fix: 'text-ribbon border-ribbon',
  pattern: 'text-recalled border-recalled',
  new: 'text-ink-lo border-rule',
  learning: 'text-ink-mid border-edge',
  consolidated: 'text-recalled border-recalled',
  stale: 'text-partial border-partial',
  native: 'text-recalled border-recalled',
  wrapped: 'text-partial border-partial',
  completed: 'text-recalled border-recalled',
  pending: 'text-ink-lo border-rule',
  running: 'text-ink-mid border-edge',
  failed: 'text-ribbon border-ribbon',
  insufficient_content: 'text-partial border-partial',
  /* provenance */
  inherited: 'text-ink-mid border-edge',
  generated: 'text-ink-lo border-edge border-dashed',
  authored: 'text-ribbon border-ribbon',
}

export function Badge({ label, className = '' }: { label: string; className?: string }) {
  const color = badgeColors[label] ?? 'text-ink-lo border-rule'
  return (
    <span
      className={
        `inline-block border px-2 py-0.5 text-[10px] uppercase tracking-[0.12em] ` +
        `whitespace-nowrap ${color} ${className}`
      }
    >
      {label.replace(/_/g, ' ')}
    </span>
  )
}

export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 text-ink-lo text-sm py-8 justify-center" role="status">
      <span
        aria-hidden="true"
        className="h-4 w-4 animate-spin border-2 border-rule border-t-ribbon"
      />
      {label ?? 'Loading…'}
    </div>
  )
}

/* Empty states carry as much design effort as populated views, and they offer
   the next action rather than apologising. (Retool; research/v2/07 §13.) */
export function EmptyState({ title, hint, action }: { title: string; hint?: string; action?: ReactNode }) {
  return (
    <div className="border border-dashed border-edge p-10 text-center">
      <p className="text-ink font-medium">{title}</p>
      {hint && <p className="text-ink-lo text-sm mt-2 max-w-md mx-auto leading-relaxed">{hint}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  )
}

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: ReactNode }) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-4 mb-6 pb-4 border-b border-rule">
      <div>
        <h1 className="font-display text-xl font-semibold text-ink lowercase tracking-tight">{title}</h1>
        {subtitle && <p className="text-ink-lo text-sm mt-1.5 max-w-2xl leading-relaxed">{subtitle}</p>}
      </div>
      {action}
    </div>
  )
}

export function ErrorNote({ message }: { message: string | null }) {
  if (!message) return null
  return (
    <div
      role="alert"
      className="border border-ribbon border-l-2 bg-surface px-4 py-2.5 text-sm text-ribbon"
    >
      {message}
    </div>
  )
}
