import { useState, type FormEvent } from 'react'
import { Button, Card, ErrorNote, Input, PageHeader } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import { api } from '../lib/api'

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
