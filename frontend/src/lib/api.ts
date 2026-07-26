/** API client: JWT bearer auth, transparent single-flight refresh on 401. */
import type { TokenResponse } from './types'

const BASE = `${import.meta.env.VITE_API_URL ?? 'http://localhost:8000'}/api/v1`

const ACCESS_KEY = 'trivium_access'
const REFRESH_KEY = 'trivium_refresh'

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_KEY)
}

export function storeTokens(tokens: TokenResponse) {
  localStorage.setItem(ACCESS_KEY, tokens.access_token)
  localStorage.setItem(REFRESH_KEY, tokens.refresh_token)
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
}

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

let refreshPromise: Promise<boolean> | null = null

async function tryRefresh(): Promise<boolean> {
  if (!refreshPromise) {
    refreshPromise = (async () => {
      const refresh = localStorage.getItem(REFRESH_KEY)
      if (!refresh) return false
      try {
        const resp = await fetch(`${BASE}/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refresh }),
        })
        if (!resp.ok) return false
        storeTokens((await resp.json()) as TokenResponse)
        return true
      } catch {
        return false
      } finally {
        refreshPromise = null
      }
    })()
  }
  return refreshPromise
}

async function parseError(resp: Response): Promise<string> {
  try {
    const data = await resp.json()
    if (typeof data.detail === 'string') return data.detail
    if (Array.isArray(data.detail)) return data.detail.map((d: { msg: string }) => d.msg).join('; ')
  } catch {
    /* fall through */
  }
  return `Request failed (${resp.status})`
}

export async function api<T>(
  path: string,
  options: { method?: string; body?: unknown; raw?: boolean } = {},
): Promise<T> {
  const doFetch = () =>
    fetch(`${BASE}${path}`, {
      method: options.method ?? 'GET',
      headers: {
        ...(options.body !== undefined ? { 'Content-Type': 'application/json' } : {}),
        ...(getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {}),
      },
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    })

  let resp = await doFetch()
  if (resp.status === 401 && localStorage.getItem(REFRESH_KEY)) {
    const refreshed = await tryRefresh()
    if (refreshed) {
      resp = await doFetch()
    } else {
      clearTokens()
      window.dispatchEvent(new Event('trivium:logout'))
    }
  }
  if (!resp.ok) throw new ApiError(resp.status, await parseError(resp))
  if (resp.status === 204) return undefined as T
  if (options.raw) return (await resp.text()) as T
  return (await resp.json()) as T
}
