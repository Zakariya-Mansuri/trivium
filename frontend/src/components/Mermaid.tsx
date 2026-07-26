import { useEffect, useRef, useState } from 'react'

let mermaidReady: Promise<typeof import('mermaid')> | null = null

function loadMermaid() {
  if (!mermaidReady) {
    mermaidReady = import('mermaid').then((m) => {
      m.default.initialize({
        startOnLoad: false,
        theme: 'dark',
        themeVariables: {
          primaryColor: '#1f2940',
          primaryTextColor: '#e3e8f2',
          primaryBorderColor: '#6172f3',
          lineColor: '#8a97b1',
          fontFamily: 'Inter, sans-serif',
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
    return <pre className="text-xs text-ink-300 bg-ink-800 rounded-lg p-4 overflow-x-auto">{chart}</pre>
  }
  return <div ref={ref} className="mermaid-container flex justify-center py-2" />
}
