/** Verify: Skills page (two reports + resources), Agent recent-chats rail, Sessions grouping. */
import { chromium } from 'playwright'

const BASE = process.env.BASE_URL || 'http://localhost:4173'
const API = (process.env.API_URL || 'http://localhost:8001') + '/api/v1'
const email = `skill-${Date.now()}@test.dev`
const results = []
const check = (name, ok, extra = '') => {
  results.push(`${ok ? 'PASS' : 'FAIL'}  ${name}${extra ? ' — ' + extra : ''}`)
  if (!ok) process.exitCode = 1
}

// Seed: user + two imported sessions (>=6 user messages) + one agent chat.
const tokens = await (
  await fetch(`${API}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password: 'SkillCheck1', display_name: 'Skill Check' }),
  })
).json()
const auth = { 'Content-Type': 'application/json', Authorization: `Bearer ${tokens.access_token}` }
const MESSAGES = [
  { role: 'user', content: 'fix my jwt auth bug in fastapi, must keep the existing bcrypt flow. return a diff only.' },
  { role: 'assistant', content: 'The signing secret differs from the verifying secret. Here is the diff...' },
  { role: 'user', content: 'now add rate limiting middleware. it should only apply to auth endpoints. show an example.' },
  { role: 'assistant', content: 'Use slowapi with a limiter keyed on remote address...' },
  { role: 'user', content: 'explain why the react useEffect cleanup pattern matters here' },
  { role: 'assistant', content: 'Cleanup prevents stale subscriptions...' },
]
for (const tool of ['claude_code', 'cursor']) {
  await fetch(`${API}/sessions/import`, {
    method: 'POST',
    headers: auth,
    body: JSON.stringify({ source_tool: tool, title: `${tool} session`, messages: MESSAGES }),
  })
}
await fetch(`${API}/agent/chat`, {
  method: 'POST',
  headers: auth,
  body: JSON.stringify({ message: 'How do I structure error handling in my python api middleware?' }),
})

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } })
page.setDefaultTimeout(25000)

try {
  await page.goto(`${BASE}/login`)
  await page.getByPlaceholder('you@example.com').fill(email)
  await page.getByPlaceholder('Password').fill('SkillCheck1')
  await page.getByRole('button', { name: 'Log in' }).click()
  await page.waitForURL('**/app')

  // Skills page: two separate reports render with scores + credible resources.
  await page.locator('aside nav').getByRole('link', { name: 'Improve' }).click()
  await page.getByText('Language report').waitFor()
  await page.getByText('Prompting report').waitFor()
  check('two separate report components render', true)
  await page.getByText('Improve with (credible sources)').nth(1).waitFor({ timeout: 45000 })
  check('language sub-scores render', await page.getByText('vocabulary', { exact: true }).isVisible())
  check('prompting sub-scores render', await page.getByText('specificity', { exact: true }).isVisible())
  await page.locator('a[href^="https://"]').first().waitFor({ timeout: 15000 })
  const resourceLinks = await page
    .locator('a[href*="ocw.mit.edu"], a[href*="coursera"], a[href*="anthropic"], a[href*="openai"], a[href*="purdue"], a[href*="google"], a[href*="promptingguide"]')
    .count()
  check('credible resources linked', resourceLinks >= 2, `${resourceLinks} links`)
  check('gaps section present', await page.getByText('Fill your knowledge gaps').isVisible())
  await page.screenshot({ path: 'e2e/shots/skills.png', fullPage: true })

  // Agent rail: recent chats listed, clicking loads the conversation.
  await page.locator('aside nav').getByRole('link', { name: 'Agent' }).click()
  await page.getByText('Recent chats').waitFor()
  const chatEntry = page.locator('button', { hasText: /error handling/ }).first()
  check('recent chats rail lists agent session', await chatEntry.isVisible())
  await chatEntry.click()
  await page.getByText(/error handling/).nth(1).waitFor()
  check('clicking a recent chat loads its messages', true)

  // Sessions grouping.
  await page.locator('aside nav').getByRole('link', { name: 'Sessions' }).click()
  await page.getByText('Today', { exact: true }).waitFor()
  check('sessions grouped by recency', true)
  check('learning-material framing note', await page.getByText(/learning material, not chat history/).isVisible())
  await page.screenshot({ path: 'e2e/shots/sessions-grouped.png' })
} catch (err) {
  check('skills check crashed', false, String(err).slice(0, 300))
  await page.screenshot({ path: 'e2e/shots/skills-fail.png', fullPage: true })
} finally {
  console.log(results.join('\n'))
  await browser.close()
}
