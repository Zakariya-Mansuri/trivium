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

export default function Mermaid({ chart }: { chart: string }) {
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
