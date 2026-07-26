import { useEffect, useRef, useState, type FormEvent } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import Markdown from '../components/Markdown'
import { Button, Card, ErrorNote, PageHeader, TextArea } from '../components/ui'
import { api } from '../lib/api'
import type { AgentChatResponse, Message, Project, Session } from '../lib/types'

export default function AgentChat() {
  const [params, setParams] = useSearchParams()
  const navigate = useNavigate()
  const sessionId = params.get('session')
  const [projects, setProjects] = useState<Project[]>([])
  const [projectId, setProjectId] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [recent, setRecent] = useState<Session[]>([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    api<Project[]>('/projects').then(setProjects)
  }, [])

  const loadRecent = () =>
    api<Session[]>('/sessions').then((all) => setRecent(all.filter((s) => s.source_tool === 'native').slice(0, 15)))
  useEffect(() => {
    loadRecent()
  }, [sessionId])

  useEffect(() => {
    if (sessionId) {
      api<{ messages: Message[] }>(`/sessions/${sessionId}`)
        .then((s) => setMessages(s.messages))
        .catch(() => setParams({}))
    } else {
      setMessages([])
    }
  }, [sessionId, setParams])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, busy])

  const send = async (e: FormEvent) => {
    e.preventDefault()
    const text = input.trim()
    if (!text || busy) return
    setBusy(true)
    setError(null)
    setInput('')
    const optimistic: Message = {
      id: 'pending',
      session_id: sessionId ?? '',
      role: 'user',
      content: text,
      authored_by: 'user',
      code_diff: null,
      timestamp: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, optimistic])
    try {
      const resp = await api<AgentChatResponse>('/agent/chat', {
        method: 'POST',
        body: { session_id: sessionId, project_id: sessionId ? undefined : projectId || null, message: text },
      })
      setMessages((prev) => [...prev.filter((m) => m.id !== 'pending'), resp.user_message, resp.assistant_message])
      if (!sessionId) setParams({ session: resp.session_id })
    } catch (err) {
      setMessages((prev) => prev.filter((m) => m.id !== 'pending'))
      setInput(text)
      setError(err instanceof Error ? err.message : 'Chat failed')
    } finally {
      setBusy(false)
    }
  }

  const endAndLearn = async () => {
    if (!sessionId) return
    setBusy(true)
    try {
      await api(`/sessions/${sessionId}/end`, { method: 'POST' })
      navigate(`/app/sessions/${sessionId}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to end session')
      setBusy(false)
    }
  }

  return (
    <div className="fade-up flex flex-col h-[calc(100vh-4rem)]">
      <PageHeader
        title="Native agent"
        subtitle="Full-fidelity capture: every turn is recorded with correct authorship, feeding your knowledge graph."
        action={
          sessionId ? (
            <div className="flex gap-2">
              <Button variant="secondary" onClick={() => setParams({})}>
                New session
              </Button>
              <Button onClick={endAndLearn} disabled={busy}>
                End session → extract
              </Button>
            </div>
          ) : (
            <select
              value={projectId}
              onChange={(e) => setProjectId(e.target.value)}
              className="rounded-lg bg-ink-800 border border-ink-600 px-3 py-2 text-sm text-ink-100 outline-none focus:border-primary-500"
              title="Attach this session to a project"
            >
              <option value="">No project</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          )
        }
      />

      <div className="flex-1 flex gap-4 min-h-0 mb-4">
        <aside className="hidden lg:flex w-52 shrink-0 flex-col card overflow-y-auto">
          <p className="text-[10px] uppercase tracking-widest text-ink-300 px-3 pt-3 pb-2">Recent chats</p>
          {recent.length === 0 && <p className="text-xs text-ink-300 px-3">No agent chats yet.</p>}
          {recent.map((s) => (
            <button
              key={s.id}
              onClick={() => setParams({ session: s.id })}
              className={`text-left px-3 py-2 border-l-2 transition-colors ${
                s.id === sessionId
                  ? 'border-primary-500 bg-primary-600/10 text-ink-100'
                  : 'border-transparent text-ink-200 hover:bg-ink-800'
              }`}
            >
              <span className="block text-xs truncate">{s.title ?? 'Untitled chat'}</span>
              <span className="block text-[10px] text-ink-300 mt-0.5">
                {new Date(s.started_at).toLocaleDateString()}
                {s.ended_at ? ' · ended' : ''}
              </span>
            </button>
          ))}
        </aside>

        <Card className="flex-1 overflow-y-auto space-y-4 min-w-0">
          {messages.length === 0 && (
            <p className="text-sm text-ink-300 text-center py-16">
              Ask a coding question — architecture, debugging, tradeoffs. Everything becomes learnable material.
            </p>
          )}
          {messages.map((m, i) => (
            <div key={`${m.id}-${i}`} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-[85%] rounded-xl px-4 py-3 text-sm leading-relaxed ${
                  m.role === 'user'
                    ? 'bg-primary-600/20 border border-primary-600/40 text-ink-100 whitespace-pre-wrap'
                    : 'bg-ink-800 border border-ink-600 text-ink-100'
                }`}
              >
                {m.role === 'user' ? m.content : <Markdown>{m.content}</Markdown>}
              </div>
            </div>
          ))}
          {busy && <p className="text-xs text-ink-300 animate-pulse">Agent is thinking…</p>}
          <div ref={bottomRef} />
        </Card>
      </div>

      <ErrorNote message={error} />
      <form onSubmit={send} className="flex gap-3 items-end mt-2">
        <TextArea
          rows={2}
          placeholder="Ask the agent… (Enter to send, Shift+Enter for newline)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              e.currentTarget.form?.requestSubmit()
            }
          }}
          maxLength={50000}
        />
        <Button type="submit" disabled={busy || !input.trim()}>
          Send
        </Button>
      </form>
    </div>
  )
}
