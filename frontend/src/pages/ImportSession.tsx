import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button, Card, ErrorNote, Input, PageHeader, TextArea } from '../components/ui'
import { api } from '../lib/api'
import type { Project, Session } from '../lib/types'

const TOOLS = ['claude_code', 'cursor', 'copilot', 'chatgpt', 'other'] as const

/** Parses "User: ..." / "Assistant: ..." (or You:/AI:) transcript text into messages. */
function parseTranscript(raw: string): { role: 'user' | 'assistant'; content: string }[] {
  const lines = raw.split(/\r?\n/)
  const messages: { role: 'user' | 'assistant'; content: string }[] = []
  let role: 'user' | 'assistant' | null = null
  let buffer: string[] = []

  const flush = () => {
    if (role && buffer.join('\n').trim()) messages.push({ role, content: buffer.join('\n').trim() })
    buffer = []
  }

  for (const line of lines) {
    const m = line.match(/^(user|you|human|assistant|ai|agent|claude|gpt)\s*[:>]\s*(.*)$/i)
    if (m) {
      flush()
      role = /^(user|you|human)$/i.test(m[1]) ? 'user' : 'assistant'
      buffer = [m[2]]
    } else {
      buffer.push(line)
    }
  }
  flush()
  return messages
}

export default function ImportSession() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState<Project[]>([])
  const [projectId, setProjectId] = useState('')
  const [tool, setTool] = useState<(typeof TOOLS)[number]>('claude_code')
  const [title, setTitle] = useState('')
  const [raw, setRaw] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    api<Project[]>('/projects').then(setProjects)
  }, [])

  const parsed = useMemo(() => parseTranscript(raw), [raw])

  const submit = async () => {
    setBusy(true)
    setError(null)
    try {
      const session = await api<Session>('/sessions/import', {
        method: 'POST',
        body: {
          project_id: projectId || null,
          source_tool: tool,
          title: title || null,
          messages: parsed,
          raw_text: raw,
        },
      })
      navigate(`/app/sessions/${session.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Import failed')
      setBusy(false)
    }
  }

  return (
    <div className="fade-up max-w-3xl">
      <PageHeader
        title="Import a session"
        subtitle="Paste a transcript from an external tool. Imported sessions are honestly tagged 'wrapped' fidelity — artifacts from them can be thinner than native-agent ones."
      />
      <Card className="space-y-4">
        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-ink-300 block mb-1.5">Source tool</label>
            <select
              value={tool}
              onChange={(e) => setTool(e.target.value as (typeof TOOLS)[number])}
              className="w-full rounded-lg bg-ink-800 border border-ink-600 px-3 py-2 text-sm text-ink-100 outline-none focus:border-primary-500"
            >
              {TOOLS.map((t) => (
                <option key={t} value={t}>
                  {t.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-ink-300 block mb-1.5">Project (optional)</label>
            <select
              value={projectId}
              onChange={(e) => setProjectId(e.target.value)}
              className="w-full rounded-lg bg-ink-800 border border-ink-600 px-3 py-2 text-sm text-ink-100 outline-none focus:border-primary-500"
            >
              <option value="">— none —</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div>
          <label className="text-xs text-ink-300 block mb-1.5">Title (optional)</label>
          <Input placeholder="e.g. Debugging the auth middleware" value={title} onChange={(e) => setTitle(e.target.value)} maxLength={300} />
        </div>
        <div>
          <label className="text-xs text-ink-300 block mb-1.5">
            Transcript — prefix lines with <code className="text-primary-300">User:</code> and{' '}
            <code className="text-primary-300">Assistant:</code>
          </label>
          <TextArea
            rows={14}
            placeholder={'User: How do I add JWT auth to FastAPI?\nAssistant: You can use PyJWT. First install it...\nUser: I got an InvalidSignatureError...'}
            value={raw}
            onChange={(e) => setRaw(e.target.value)}
          />
          <p className="text-xs text-ink-300 mt-1.5">
            {parsed.length > 0
              ? `Parsed ${parsed.length} message${parsed.length === 1 ? '' : 's'} (${parsed.filter((m) => m.role === 'user').length} user / ${parsed.filter((m) => m.role === 'assistant').length} assistant)`
              : 'No messages parsed yet — check the User:/Assistant: prefixes.'}
          </p>
        </div>
        <ErrorNote message={error} />
        <Button onClick={submit} disabled={busy || parsed.length === 0}>
          {busy ? 'Importing & extracting…' : 'Import session'}
        </Button>
      </Card>
    </div>
  )
}
