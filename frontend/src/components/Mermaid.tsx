import { useEffect, useRef, useState } from 'react'

let mermaidReady: Promise<typeof import('mermaid')> | null = null

/** Reads a design token from the stylesheet so Mermaid can never drift from
 *  index.css. The shipped version hard-coded five hex values and a font name
 *  in JavaScript, which would silently diverge on the first palette change. */
function token(name: string, fallback: string): string {
  if (typeof window === 'undefined') return fallback
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  return v || fallback
}

function loadMermaid() {
  if (!mermaidReady) {
    mermaidReady = import('mermaid').then((m) => {
      m.default.initialize({
        startOnLoad: false,
        theme: 'base',
        themeVariables: {
          background: token('--color-paper', '#f4f2ec'),
          primaryColor: token('--color-surface', '#e9e5de'),
          primaryTextColor: token('--color-ink', '#14120f'),
          primaryBorderColor: token('--color-edge', '#85807a'),
          secondaryColor: token('--color-surface', '#e9e5de'),
          tertiaryColor: token('--color-paper', '#f4f2ec'),
          lineColor: token('--color-ink-mid', '#4e4a42'),
          textColor: token('--color-ink-mid', '#4e4a42'),
          fontFamily: token('--font-mono', 'ui-monospace, monospace'),
          fontSize: '13px',
        },
      })
      return m
    })
  }
  return mermaidReady
}

let renderCounter = 0

/** Repairs common LLM mermaid mistakes (mirrors the backend sanitizer) so
 * previously stored diagrams render too: strips code fences, quotes node
 * labels containing special characters, ensures a flowchart header. */
export function sanitizeMermaid(spec: string): string {
  let s = spec.trim()
  const fence = s.match(/^```(?:mermaid)?\s*\n([\s\S]*?)\n?```$/)
  if (fence) s = fence[1].trim()
  if (!/^(flowchart|graph)\b/.test(s)) s = 'flowchart TD\n' + s
  return s.replace(/\b([A-Za-z0-9_]+)\[(?!")([^\]]*)\]/g, (_m, id: string, label: string) => {
    return `${id}["${label.replace(/"/g, "'").trim()}"]`
  })
}

export default function Mermaid({ chart: rawChart }: { chart: string }) {
  const chart = sanitizeMermaid(rawChart)
  const ref = useRef<HTMLDivElement>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    let cancelled = false
    loadMermaid()
      .then(async (m) => {
        const { svg } = await m.default.render(`trivium-mmd-${renderCounter++}`, chart)
        if (!cancelled && ref.current) ref.current.innerHTML = svg
      })
      .catch(() => {
        if (!cancelled) setError(true)
      })
    return () => {
      cancelled = true
    }
  }, [chart])

  if (error) {
    return <pre className="text-xs text-ink-lo bg-surface border border-rule p-4 overflow-x-auto">{chart}</pre>
  }
  /* .mermaid-container reserves a min-height in index.css: the shipped version
     injected SVG into a zero-height div, which was a guaranteed layout shift. */
  return <div ref={ref} className="mermaid-container py-2" />
}
