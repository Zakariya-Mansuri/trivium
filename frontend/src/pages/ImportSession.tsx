import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button, Card, ErrorNote, Input, PageHeader, TextArea } from '../components/ui'
import { api } from '../lib/api'
import type { Project, Session } from '../lib/types'

const TOOLS = ['claude', 'chatgpt', 'claude_code', 'cursor', 'copilot', 'gemini', 'other'] as const

type ParsedMessage = { role: 'user' | 'assistant'; content: string }

/** ChatGPT conversations.json export: {"mapping": {id: {message: {...}}}}. */
function parseChatGPTExport(data: Record<string, unknown>): ParsedMessage[] {
  const mapping = data.mapping
  if (!mapping || typeof mapping !== 'object') return []
  const entries: { t: number; m: ParsedMessage }[] = []
  for (const node of Object.values(mapping as Record<string, { message?: Record<string, unknown> }>)) {
    const msg = node?.message
    if (!msg) continue
    const role = (msg.author as { role?: string } | undefined)?.role
    const content = msg.content as { parts?: unknown[] } | undefined
    const text = (content?.parts ?? []).filter((p) => typeof p === 'string').join('\n').trim()
    if ((role === 'user' || role === 'assistant') && text) {
      entries.push({ t: (msg.create_time as number) ?? 0, m: { role, content: text } })
    }
  }
  return entries.sort((a, b) => a.t - b.t).map((e) => e.m)
}

function cleanMessages(list: unknown[]): ParsedMessage[] {
  const out: ParsedMessage[] = []
  for (const item of list) {
    const m = item as { role?: string; content?: string }
    if ((m?.role === 'user' || m?.role === 'assistant') && typeof m.content === 'string' && m.content.trim()) {
      out.push({ role: m.role, content: m.content.trim() })
    }
  }
  return out
}

/** Accepts JSON exports (ChatGPT conversations.json, [{role,content}], {messages}) or prefixed text. */
function parseTranscript(raw: string): ParsedMessage[] {
  const trimmed = raw.trim()
  if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
    try {
      const data = JSON.parse(trimmed)
      if (Array.isArray(data)) {
        if (data[0] && typeof data[0] === 'object' && 'mapping' in data[0]) return parseChatGPTExport(data[0])
        return cleanMessages(data)
      }
      if (data && typeof data === 'object') {
        if ('mapping' in data) return parseChatGPTExport(data)
        if (Array.isArray(data.messages)) return cleanMessages(data.messages)
      }
    } catch {
      /* not JSON — fall through to text parsing */
    }
  }

  const messages: ParsedMessage[] = []
  let role: 'user' | 'assistant' | null = null
  let buffer: string[] = []
  const flush = () => {
    if (role && buffer.join('\n').trim()) messages.push({ role, content: buffer.join('\n').trim() })
    buffer = []
  }
  for (const line of raw.split(/\r?\n/)) {
    const m = line.match(/^\s*(user|you|human|me|assistant|ai|agent|claude|chatgpt|gpt|gemini|copilot)\s*[:>]\s*(.*)$/i)
    if (m) {
      flush()
      role = /^(user|you|human|me)$/i.test(m[1]) ? 'user' : 'assistant'
      buffer = [m[2]]
    } else if (role !== null) {
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
      <Card className="mb-4 border-primary-600/40 !py-4">
        <p className="text-sm text-ink-200">
          <span className="text-primary-300 font-medium">⚡ One-click import:</span> install the{' '}
          <span className="text-ink-100 font-medium">Trivium Companion</span> browser extension (in the repo's{' '}
          <code className="text-primary-300">extension/</code> folder) to pull any open ChatGPT or Claude
          conversation straight into Trivium — no copy-pasting at all.
        </p>
      </Card>
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
            Transcript — <code className="text-primary-300">User:</code>/<code className="text-primary-300">Assistant:</code>{' '}
            prefixed text, a ChatGPT <code className="text-primary-300">conversations.json</code> export, or any{' '}
            <code className="text-primary-300">{'[{role, content}]'}</code> JSON
          </label>
          <TextArea
            rows={14}
            placeholder={'User: How do I add JWT auth to FastAPI?\nAssistant: You can use PyJWT. First install it...\nUser: I got an InvalidSignatureError...\n\n…or paste an exported JSON file\'s contents here.'}
            value={raw}
            onChange={(e) => setRaw(e.target.value)}
          />
          <p className="text-xs text-ink-300 mt-1.5">
            {parsed.length > 0
              ? `Parsed ${parsed.length} message${parsed.length === 1 ? '' : 's'} (${parsed.filter((m) => m.role === 'user').length} user / ${parsed.filter((m) => m.role === 'assistant').length} assistant)`
              : 'No messages parsed yet — use User:/Assistant: prefixes, or paste an exported JSON.'}
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
