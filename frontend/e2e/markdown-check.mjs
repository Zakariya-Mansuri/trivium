/** Visual check: assistant markdown renders (code fence, list, bold, table). */
import { chromium } from 'playwright'

const BASE = process.env.BASE_URL || 'http://localhost:5173'
const API = 'http://localhost:8000/api/v1'
const email = `md-${Date.now()}@test.dev`

const MD = `Here's how to fix your JWT bug:

## Root cause

The **signing secret** differs from the *verifying* secret.

1. Load \`SECRET_KEY\` from one config source
2. Never hardcode a fallback
3. Rotate the key after fixing

\`\`\`python
import jwt

def verify(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
\`\`\`

| Option | Tradeoff |
|---|---|
| JWT | Stateless, needs refresh rotation |
| Sessions | Server state, easy revocation |

> Desirable difficulty: understand *why* before copying the fix.`

// Seed data via API directly (rendering is what we're testing).
const signup = await fetch(`${API}/auth/signup`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password: 'MdCheck123', display_name: 'MD Check' }),
})
const tokens = await signup.json()
const imp = await fetch(`${API}/sessions/import`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${tokens.access_token}` },
  body: JSON.stringify({
    source_tool: 'chatgpt',
    title: 'Markdown render check',
    messages: [
      { role: 'user', content: 'Why does my JWT verification fail?' },
      { role: 'assistant', content: MD },
    ],
  }),
})
const session = await imp.json()
console.log('session created:', session.id)

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1360, height: 1100 } })
await page.goto(`${BASE}/login`)
await page.getByPlaceholder('you@example.com').fill(email)
await page.getByPlaceholder('Password').fill('MdCheck123')
await page.getByRole('button', { name: 'Log in' }).click()
await page.waitForURL('**/app')
await page.goto(`${BASE}/app/sessions/${session.id}`)
await page.waitForSelector('text=Root cause')
await page.screenshot({ path: 'e2e/shots/markdown-session.png', fullPage: true })
console.log('screenshot saved')

// Assertions: markdown became real elements, not literal syntax.
const checks = [
  ['h2 rendered', await page.locator('.md-body h2', { hasText: 'Root cause' }).count()],
  ['code block rendered', await page.locator('.md-body pre code').count()],
  ['ordered list rendered', await page.locator('.md-body ol > li').count()],
  ['table rendered', await page.locator('.md-body table td').count()],
  ['bold rendered', await page.locator('.md-body strong', { hasText: 'signing secret' }).count()],
  ['blockquote rendered', await page.locator('.md-body blockquote').count()],
]
let fail = false
for (const [name, count] of checks) {
  const ok = count > 0
  if (!ok) fail = true
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name} (${count})`)
}
const literal = await page.locator('.md-body', { hasText: '```' }).count()
console.log(`${literal === 0 ? 'PASS' : 'FAIL'}  no literal \`\`\` fences visible`)
if (literal > 0) fail = true
process.exitCode = fail ? 1 : 0
await browser.close()
