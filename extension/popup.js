/* global chrome */
const $ = (id) => document.getElementById(id)

const send = (msg) =>
  new Promise((resolve) => {
    chrome.runtime.sendMessage(msg, (resp) => {
      resolve(resp ?? { ok: false, error: chrome.runtime.lastError?.message || 'No response' })
    })
  })

function setStatus(el, kind, text) {
  el.className = `status ${kind}`
  el.textContent = text
}

function detectLabel(url) {
  try {
    const u = new URL(url)
    if (u.hostname === 'claude.ai' && /^\/chat\/[0-9a-f-]{36}/i.test(u.pathname)) return 'Claude conversation'
    if (
      (u.hostname === 'chatgpt.com' || u.hostname === 'chat.openai.com') &&
      /^\/(c|share)\//.test(u.pathname)
    )
      return 'ChatGPT conversation'
  } catch {
    /* not a URL */
  }
  return null
}

async function currentTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })
  return tab
}

async function refresh() {
  const status = await send({ type: 'status' })
  if (!status.ok) {
    $('view-login').style.display = 'block'
    setStatus($('loginStatus'), 'err', status.error)
    return
  }
  if (!status.loggedIn) {
    $('view-login').style.display = 'block'
    $('view-app').style.display = 'none'
    $('apiUrl').value = status.apiUrl || 'https://trivium-api.onrender.com'
    return
  }
  $('view-login').style.display = 'none'
  $('view-app').style.display = 'block'
  $('who').textContent = status.email

  const select = $('project')
  select.innerHTML = '<option value="">— none —</option>'
  for (const p of status.projects || []) {
    const opt = document.createElement('option')
    opt.value = p.id
    opt.textContent = p.name
    select.appendChild(opt)
  }
  const { lastProjectId } = await chrome.storage.local.get('lastProjectId')
  if (lastProjectId) select.value = lastProjectId

  const tab = await currentTab()
  const label = tab?.url ? detectLabel(tab.url) : null
  if (label) {
    $('pageInfo').innerHTML = `Detected: <b>${label}</b>`
    $('importBtn').disabled = false
  } else {
    $('pageInfo').textContent = 'Open a ChatGPT (chatgpt.com/c/…) or Claude (claude.ai/chat/…) conversation tab, then click the extension.'
    $('importBtn').disabled = true
  }
}

$('loginBtn').addEventListener('click', async () => {
  $('loginBtn').disabled = true
  setStatus($('loginStatus'), 'ok', 'Logging in…')
  const resp = await send({
    type: 'login',
    apiUrl: $('apiUrl').value.trim() || 'https://trivium-api.onrender.com',
    email: $('email').value.trim(),
    password: $('password').value,
  })
  $('loginBtn').disabled = false
  if (resp.ok) {
    $('loginStatus').className = 'status'
    await refresh()
  } else {
    setStatus($('loginStatus'), 'err', resp.error)
  }
})

$('logoutBtn').addEventListener('click', async () => {
  await send({ type: 'logout' })
  await refresh()
})

$('importBtn').addEventListener('click', async () => {
  const tab = await currentTab()
  if (!tab?.url) return
  $('importBtn').disabled = true
  setStatus($('importStatus'), 'ok', 'Extracting conversation…')
  await chrome.storage.local.set({ lastProjectId: $('project').value })
  const resp = await send({ type: 'import', url: tab.url, projectId: $('project').value || null })
  $('importBtn').disabled = false
  if (resp.ok) {
    setStatus(
      $('importStatus'),
      'ok',
      `Imported ${resp.count} messages${resp.title ? ` from "${resp.title}"` : ''}. Extraction is running — open Trivium to Learn from it.`,
    )
  } else if (resp.error === 'PLATFORM_NOT_LOGGED_IN') {
    setStatus($('importStatus'), 'err', 'You are not logged in to this platform in the browser — log in on the site first.')
  } else {
    setStatus($('importStatus'), 'err', resp.error)
  }
})

refresh()
