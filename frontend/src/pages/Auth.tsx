import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button, ErrorNote, Input } from '../components/ui'
import { useAuth } from '../context/AuthContext'

function AuthShell({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-ink-950">
      <div className="w-full max-w-sm">
        <Link to="/" className="block text-center font-display text-xl font-bold mb-8">
          <span className="text-primary-400">▲</span> Trivium
        </Link>
        <div className="card p-7">
          <h1 className="font-display text-xl font-semibold text-ink-100">{title}</h1>
          <p className="text-sm text-ink-300 mt-1 mb-6">{subtitle}</p>
          {children}
        </div>
      </div>
    </div>
  )
}

export function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await login(email, password)
      navigate('/app')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthShell title="Welcome back" subtitle="Pick up where your knowledge left off.">
      <form onSubmit={submit} className="space-y-4">
        <Input type="email" required placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" />
        <Input type="password" required placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" />
        <ErrorNote message={error} />
        <Button type="submit" disabled={busy} className="w-full">
          {busy ? 'Logging in…' : 'Log in'}
        </Button>
      </form>
      <p className="text-sm text-ink-300 mt-5 text-center">
        New here?{' '}
        <Link to="/signup" className="text-primary-300 hover:text-primary-400">
          Create an account
        </Link>
      </p>
    </AuthShell>
  )
}

export function Signup() {
  const { signup } = useAuth()
  const navigate = useNavigate()
  const [displayName, setDisplayName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await signup(email, password, displayName)
      navigate('/app')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Signup failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthShell title="Create your account" subtitle="Start building durable knowledge from your coding.">
      <form onSubmit={submit} className="space-y-4">
        <Input placeholder="Display name (optional)" value={displayName} onChange={(e) => setDisplayName(e.target.value)} autoComplete="name" />
        <Input type="email" required placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" />
        <Input
          type="password"
          required
          placeholder="Password — 8+ chars, letters and digits"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="new-password"
        />
        <ErrorNote message={error} />
        <Button type="submit" disabled={busy} className="w-full">
          {busy ? 'Creating…' : 'Sign up'}
        </Button>
      </form>
      <p className="text-sm text-ink-300 mt-5 text-center">
        Already have an account?{' '}
        <Link to="/login" className="text-primary-300 hover:text-primary-400">
          Log in
        </Link>
      </p>
    </AuthShell>
  )
}
