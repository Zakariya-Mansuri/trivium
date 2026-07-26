import { useEffect, useState, type FormEvent } from 'react'
import { Button, Card, ErrorNote, Input, PageHeader } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import { api } from '../lib/api'

interface ProviderInfo {
  name: string
  label: string
  default_model: string
  keys_url: string
  free_tier: boolean
}

interface LLMConfig {
  provider: string | null
  model: string | null
  key_hint: string | null
  source: 'user' | 'server_default'
  active_label: string
}

/** Attach your own AI provider (BYOK) — OpenCode-style, per account. */
function ProviderCard() {
  const [catalog, setCatalog] = useState<ProviderInfo[]>([])
  const [config, setConfig] = useState<LLMConfig | null>(null)
  const [provider, setProvider] = useState('groq')
  const [model, setModel] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [msg, setMsg] = useState<string | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const load = async () => {
    const [cat, cfg] = await Promise.all([
      api<{ providers: ProviderInfo[] }>('/auth/me/llm/providers'),
      api<LLMConfig>('/auth/me/llm'),
    ])
    setCatalog(cat.providers)
    setConfig(cfg)
    if (cfg.provider) {
      setProvider(cfg.provider)
      setModel(cfg.model ?? '')
    }
  }
  useEffect(() => {
    load().catch((e) => setErr(e.message))
  }, [])

  const selected = catalog.find((p) => p.name === provider)

  const save = async (e: FormEvent) => {
    e.preventDefault()
    setBusy(true)
    setErr(null)
    setMsg(null)
    try {
      const cfg = await api<LLMConfig>('/auth/me/llm', {
        method: 'PUT',
        body: { provider, model: model.trim() || null, api_key: apiKey },
      })
      setConfig(cfg)
      setApiKey('')
      setMsg(`Saved — Trivium now uses ${cfg.active_label} (${cfg.key_hint}).`)
    } catch (error) {
      setErr(error instanceof Error ? error.message : 'Save failed')
    } finally {
      setBusy(false)
    }
  }

  const testConnection = async () => {
    setBusy(true)
    setErr(null)
    setMsg(null)
    try {
      const result = await api<{ ok: boolean; provider: string; model?: string; error?: string; note?: string }>(
        '/auth/me/llm/test',
        { method: 'POST' },
      )
      if (result.ok) setMsg(`✓ ${result.provider}${result.model ? ` (${result.model})` : ''} is working. ${result.note ?? ''}`)
      else setErr(`Connection failed: ${result.error}`)
    } catch (error) {
      setErr(error instanceof Error ? error.message : 'Test failed')
    } finally {
      setBusy(false)
    }
  }

  const remove = async () => {
    setBusy(true)
    setErr(null)
    try {
      setConfig(await api<LLMConfig>('/auth/me/llm', { method: 'DELETE' }))
      setMsg('Removed — back to the server default.')
    } catch (error) {
      setErr(error instanceof Error ? error.message : 'Remove failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Card>
      <h2 className="font-display font-semibold text-ink-100 mb-1">AI provider</h2>
      <p className="text-xs text-ink-300 mb-4">
        Attach your own key — extraction, artifacts, grading and reports run on <em>your</em> quota.
        {config && (
          <>
            {' '}
            Currently: <span className="text-ink-100">{config.active_label}</span>
            {config.key_hint ? ` (${config.key_hint})` : ''}
          </>
        )}
      </p>
      <form onSubmit={save} className="space-y-4">
        <div>
          <label className="text-xs text-ink-300 block mb-1.5">Provider</label>
          <select
            value={provider}
            onChange={(e) => {
              setProvider(e.target.value)
              setModel('')
            }}
            className="w-full rounded-lg bg-ink-800 border border-ink-600 px-3 py-2 text-sm text-ink-100 outline-none focus:border-primary-500"
          >
            {catalog.map((p) => (
              <option key={p.name} value={p.name}>
                {p.label}
                {p.free_tier ? ' (free tier available)' : ''}
              </option>
            ))}
          </select>
          {selected && (
            <p className="text-xs text-ink-300 mt-1.5">
              Get a key:{' '}
              <a href={selected.keys_url} target="_blank" rel="noopener noreferrer" className="text-primary-300 hover:text-primary-400">
                {selected.keys_url.replace('https://', '')}
              </a>
            </p>
          )}
        </div>
        <div>
          <label className="text-xs text-ink-300 block mb-1.5">Model (optional)</label>
          <Input
            placeholder={selected ? `default: ${selected.default_model}` : 'provider default'}
            value={model}
            onChange={(e) => setModel(e.target.value)}
            maxLength={120}
          />
        </div>
        <div>
          <label className="text-xs text-ink-300 block mb-1.5">API key — stored encrypted, never shown again</label>
          <Input
            type="password"
            placeholder={config?.key_hint ? `saved (${config.key_hint}) — enter a new key to replace` : 'paste your API key'}
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            autoComplete="off"
          />
        </div>
        <ErrorNote message={err} />
        {msg && <p className="text-sm text-good-500">{msg}</p>}
        <div className="flex flex-wrap gap-2">
          <Button type="submit" disabled={busy || apiKey.length < 8}>
            Save key
          </Button>
          <Button type="button" variant="secondary" onClick={testConnection} disabled={busy}>
            Test connection
          </Button>
          {config?.source === 'user' && (
            <Button type="button" variant="danger" onClick={remove} disabled={busy}>
              Remove
            </Button>
          )}
        </div>
      </form>
    </Card>
  )
}

export default function Settings() {
  const { user, refreshUser } = useAuth()
  const [displayName, setDisplayName] = useState(user?.display_name ?? '')
  const [intensity, setIntensity] = useState(user?.learning_intensity ?? 'balanced')
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [currentPw, setCurrentPw] = useState('')
  const [newPw, setNewPw] = useState('')
  const [pwMsg, setPwMsg] = useState<string | null>(null)
  const [pwErr, setPwErr] = useState<string | null>(null)

  const saveProfile = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setSaved(false)
    try {
      await api('/auth/me', { method: 'PATCH', body: { display_name: displayName || null, learning_intensity: intensity } })
      await refreshUser()
      setSaved(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Save failed')
    }
  }

  const changePassword = async (e: FormEvent) => {
    e.preventDefault()
    setPwErr(null)
    setPwMsg(null)
    try {
      await api('/auth/change-password', { method: 'POST', body: { current_password: currentPw, new_password: newPw } })
      setPwMsg('Password changed. Other devices have been signed out.')
      setCurrentPw('')
      setNewPw('')
    } catch (err) {
      setPwErr(err instanceof Error ? err.message : 'Change failed')
    }
  }

  return (
    <div className="fade-up max-w-xl space-y-6">
      <PageHeader title="Settings" />

      <Card>
        <h2 className="font-display font-semibold text-ink-100 mb-4">Profile</h2>
        <form onSubmit={saveProfile} className="space-y-4">
          <div>
            <label className="text-xs text-ink-300 block mb-1.5">Display name</label>
            <Input value={displayName} onChange={(e) => setDisplayName(e.target.value)} maxLength={100} />
          </div>
          <div>
            <label className="text-xs text-ink-300 block mb-1.5">Learning intensity</label>
            <div className="flex gap-2">
              {['light', 'balanced', 'intense'].map((v) => (
                <button
                  key={v}
                  type="button"
                  onClick={() => setIntensity(v)}
                  className={`rounded-lg border px-4 py-2 text-sm capitalize transition-colors ${
                    intensity === v ? 'border-primary-500 bg-primary-600/15 text-primary-300' : 'border-ink-600 text-ink-200 hover:bg-ink-800'
                  }`}
                >
                  {v}
                </button>
              ))}
            </div>
          </div>
          <ErrorNote message={error} />
          {saved && <p className="text-sm text-good-500">Saved.</p>}
          <Button type="submit">Save</Button>
        </form>
      </Card>

      <ProviderCard />

      <Card>
        <h2 className="font-display font-semibold text-ink-100 mb-4">Change password</h2>
        <form onSubmit={changePassword} className="space-y-4">
          <Input
            type="password"
            placeholder="Current password"
            value={currentPw}
            onChange={(e) => setCurrentPw(e.target.value)}
            autoComplete="current-password"
            required
          />
          <Input
            type="password"
            placeholder="New password — 8+ chars, letters and digits"
            value={newPw}
            onChange={(e) => setNewPw(e.target.value)}
            autoComplete="new-password"
            required
          />
          <ErrorNote message={pwErr} />
          {pwMsg && <p className="text-sm text-good-500">{pwMsg}</p>}
          <Button type="submit" variant="secondary">
            Change password
          </Button>
        </form>
      </Card>

      <Card>
        <h2 className="font-display font-semibold text-ink-100 mb-2">Account</h2>
        <p className="text-sm text-ink-300">
          Signed in as <span className="text-ink-100">{user?.email}</span>
        </p>
      </Card>
    </div>
  )
}
