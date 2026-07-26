/**
 * Trivium Companion — background service worker.
 * Fetches conversations from the platform's own API (using the browser's
 * logged-in cookies) and imports them into Trivium. Purely programmatic.
 */
import { detectChatPage, parseChatGPTConversation, parseClaudeConversation } from './lib/extractors.js'

const DEFAULT_API = 'http://localhost:8000'

// --- Trivium API helpers ---

async function getConfig() {
  const stored = await chrome.storage.local.get(['apiUrl', 'accessToken', 'refreshToken'])
  return {
    apiUrl: (stored.apiUrl || DEFAULT_API).replace(/\/+$/, ''),
    accessToken: stored.accessToken || null,
    refreshToken: stored.refreshToken || null,
  }
}

async function triviumFetch(path, options = {}, retry = true) {
  const cfg = await getConfig()
  if (!cfg.accessToken) throw new Error('NOT_LOGGED_IN')
  const resp = await fetch(`${cfg.apiUrl}/api/v1${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${cfg.accessToken}`,
      ...(options.headers || {}),
    },
  })
  if (resp.status === 401 && retry && cfg.refreshToken) {
    const refreshed = await fetch(`${cfg.apiUrl}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: cfg.refreshToken }),
    })
    if (refreshed.ok) {
      const tokens = await refreshed.json()
      await chrome.storage.local.set({ accessToken: tokens.access_token, refreshToken: tokens.refresh_token })
      return triviumFetch(path, options, false)
    }
    await chrome.storage.local.remove(['accessToken', 'refreshToken'])
    throw new Error('NOT_LOGGED_IN')
  }
  if (!resp.ok) {
    let detail = `Trivium API error (${resp.status})`
    try {
      const body = await resp.json()
      if (typeof body.detail === 'string') detail = body.detail
    } catch {
      /* keep generic */
    }
    throw new Error(detail)
  }
  return resp.status === 204 ? null : resp.json()
}

// --- Platform extraction ---

async function platformGet(url, headers = {}) {
  const resp = await fetch(url, { headers, credentials: 'include' })
  if (resp.status === 401 || resp.status === 403) throw new Error('PLATFORM_NOT_LOGGED_IN')
  if (!resp.ok) throw new Error(`The platform API returned ${resp.status}`)
  return resp.json()
}

async function extractClaude(conversationId) {
  const orgs = await platformGet('https://claude.ai/api/organizations')
  if (!Array.isArray(orgs) || orgs.length === 0) throw new Error('PLATFORM_NOT_LOGGED_IN')
  const org =
    orgs.find((o) => (o.capabilities || []).includes('chat')) ??
    orgs.find((o) => !(o.capabilities || []).includes('raven')) ??
    orgs[0]
  const data = await platformGet(
    `https://claude.ai/api/organizations/${org.uuid}/chat_conversations/${conversationId}?tree=False&rendering_mode=messages&render_all_tools=true`,
  )
  return parseClaudeConversation(data)
}

async function extractChatGPT(conversationId, isShare, origin) {
  const base = origin === 'chat.openai.com' ? 'https://chat.openai.com' : 'https://chatgpt.com'
  const session = await platformGet(`${base}/api/auth/session`)
  const token = session?.accessToken
  if (!token) throw new Error('PLATFORM_NOT_LOGGED_IN')
  const endpoint = isShare ? `${base}/backend-api/share/${conversationId}` : `${base}/backend-api/conversation/${conversationId}`
  const data = await platformGet(endpoint, { Authorization: `Bearer ${token}` })
  return parseChatGPTConversation(data)
}

// --- Message handling ---

chrome.runtime.onMessage.addListener((request, _sender, sendResponse) => {
  handle(request)
    .then((result) => sendResponse({ ok: true, ...result }))
    .catch((err) => sendResponse({ ok: false, error: err?.message || String(err) }))
  return true // async response
})

async function handle(request) {
  if (request.type === 'login') {
    const apiUrl = (request.apiUrl || DEFAULT_API).replace(/\/+$/, '')
    const resp = await fetch(`${apiUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: request.email, password: request.password }),
    })
    if (!resp.ok) {
      let detail = 'Login failed'
      try {
        detail = (await resp.json()).detail ?? detail
      } catch {
        /* keep generic */
      }
      throw new Error(typeof detail === 'string' ? detail : 'Login failed')
    }
    const tokens = await resp.json()
    await chrome.storage.local.set({
      apiUrl,
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
    })
    return {}
  }

  if (request.type === 'logout') {
    await chrome.storage.local.remove(['accessToken', 'refreshToken'])
    return {}
  }

  if (request.type === 'status') {
    const cfg = await getConfig()
    if (!cfg.accessToken) return { loggedIn: false, apiUrl: cfg.apiUrl }
    try {
      const me = await triviumFetch('/auth/me')
      const projects = await triviumFetch('/projects')
      return { loggedIn: true, apiUrl: cfg.apiUrl, email: me.email, projects }
    } catch (err) {
      if (err.message === 'NOT_LOGGED_IN') return { loggedIn: false, apiUrl: cfg.apiUrl }
      throw err
    }
  }

  if (request.type === 'import') {
    const page = detectChatPage(request.url)
    if (!page) throw new Error('Open a ChatGPT or Claude conversation tab first')

    let extracted
    if (page.platform === 'claude') {
      extracted = await extractClaude(page.conversationId)
    } else {
      extracted = await extractChatGPT(page.conversationId, page.isShare, new URL(request.url).hostname)
    }
    if (!extracted.messages.length) throw new Error('No messages found in this conversation')

    const session = await triviumFetch('/sessions/import', {
      method: 'POST',
      body: JSON.stringify({
        project_id: request.projectId || null,
        source_tool: page.platform,
        title: extracted.title,
        messages: extracted.messages,
      }),
    })
    return { sessionId: session.id, count: extracted.messages.length, title: extracted.title }
  }

  throw new Error(`Unknown request type: ${request.type}`)
}
