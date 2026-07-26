import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import { api, clearTokens, getAccessToken, storeTokens } from '../lib/api'
import type { TokenResponse, User } from '../lib/types'

interface AuthState {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, displayName: string) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    if (!getAccessToken()) {
      setUser(null)
      setLoading(false)
      return
    }
    try {
      setUser(await api<User>('/auth/me'))
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refreshUser()
    const onLogout = () => setUser(null)
    window.addEventListener('trivium:logout', onLogout)
    return () => window.removeEventListener('trivium:logout', onLogout)
  }, [refreshUser])

  const login = useCallback(
    async (email: string, password: string) => {
      const tokens = await api<TokenResponse>('/auth/login', { method: 'POST', body: { email, password } })
      storeTokens(tokens)
      await refreshUser()
    },
    [refreshUser],
  )

  const signup = useCallback(
    async (email: string, password: string, displayName: string) => {
      const tokens = await api<TokenResponse>('/auth/signup', {
        method: 'POST',
        body: { email, password, display_name: displayName || null },
      })
      storeTokens(tokens)
      await refreshUser()
    },
    [refreshUser],
  )

  const logout = useCallback(async () => {
    const refresh = localStorage.getItem('trivium_refresh')
    try {
      if (refresh) await api('/auth/logout', { method: 'POST', body: { refresh_token: refresh } })
    } catch {
      /* token may already be invalid — clearing locally is what matters */
    }
    clearTokens()
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
