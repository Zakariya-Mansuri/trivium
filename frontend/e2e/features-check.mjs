/** Verify: flashcard flip UX, MCQ player, diagram rendering, early review flow. */
import { chromium } from 'playwright'

const BASE = process.env.BASE_URL || 'http://localhost:5173'
const API = (process.env.API_URL || 'http://localhost:8000') + '/api/v1'
const email = `feat-${Date.now()}@test.dev`
const results = []
const check = (name, ok, extra = '') => {
  results.push(`${ok ? 'PASS' : 'FAIL'}  ${name}${extra ? ' — ' + extra : ''}`)
  if (!ok) process.exitCode = 1
}

// Seed: user + session with concept/decision/bug/architecture content.
const signup = await fetch(`${API}/auth/signup`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password: 'FeatCheck123', display_name: 'Feat Check' }),
})
const tokens = (await signup.json())
const auth = { 'Content-Type': 'application/json', Authorization: `Bearer ${tokens.access_token}` }
const imp = await fetch(`${API}/sessions/import`, {
  method: 'POST',
  headers: auth,
  body: JSON.stringify({
    source_tool: 'chatgpt',
    title: 'Feature check session',
    messages: [
      { role: 'user', content: 'How should I expose my local uvicorn server to the network? What about the firewall?' },
      { role: 'assistant', content: 'Bind uvicorn to 0.0.0.0 instead of 127.0.0.1 using --host. The tradeoff: any device on the network can reach it, so allow python through the Windows firewall deliberately. The architecture has three components: the uvicorn server layer, the firewall module, and the router port-forwarding service in the pipeline.' },
      { role: 'user', content: 'I got an error - connection refused when hitting it from my phone.' },
      { role: 'assistant', content: 'That bug means the firewall blocked the inbound port. The fix: add an inbound rule for python on port 8000. Same pattern as before with blocked ports in your react project.' },
    ],
  }),
})
const session = await imp.json()
console.log('session:', session.id)

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } })
page.setDefaultTimeout(25000)

try {
  await page.goto(`${BASE}/login`)
  await page.getByPlaceholder('you@example.com').fill(email)
  await page.getByPlaceholder('Password').fill('FeatCheck123')
  await page.getByRole('button', { name: 'Log in' }).click()
  await page.waitForURL('**/app')

  // Learn on the session (real Groq calls; retries absorb 429s).
  await page.goto(`${BASE}/app/sessions/${session.id}`)
  await page.getByRole('button', { name: /Learn this chat/ }).click()
  await page.getByText('Learning artifacts').waitFor({ timeout: 120000 })

  // Flashcard: flip UX, no attempt gate.
  const flip = page.getByRole('button', { name: 'Flip card' }).first()
  const hasFlashcard = await flip.isVisible().catch(() => false)
  check('flashcard shows flip UI (no forced typing)', hasFlashcard)
  if (hasFlashcard) {
    await flip.click()
    check('flashcard flips to back', await page.getByText('Back', { exact: true }).first().isVisible())
  }

  // MCQ: choice buttons present, instant feedback on click.
  const choiceA = page.locator('button', { hasText: /^A\./ }).first()
  check('mcq choices rendered', await choiceA.isVisible().catch(() => false))
  await choiceA.click()
  const feedback = await page
    .getByText(/Correct\.|Not quite/)
    .first()
    .isVisible()
    .catch(() => false)
  check('mcq gives instant feedback', feedback)

  // Diagram (if the scope produced one): must render as SVG, not raw text.
  const mermaidSvg = await page.locator('.mermaid-container svg').count()
  const rawFallback = await page.locator('pre', { hasText: 'flowchart' }).count()
  check('diagram renders as SVG (no raw mermaid text)', rawFallback === 0, `svg=${mermaidSvg} raw=${rawFallback}`)

  // Early review: banner link -> early queue -> grade one item immediately.
  await page.goto(`${BASE}/app/review?early=1`)
  await page.waitForSelector('text=/1 of \\d+|Nothing due/')
  const hasItems = await page.getByText(/1 of \d+/).isVisible().catch(() => false)
  check('early queue has items right after learning', hasItems)
  if (hasItems) {
    check('early flag shown honestly', await page.getByText(/early — spacing works better/).isVisible())
    // Work through the first artifact until a grade is submitted (terminal action).
    let graded = false
    for (let step = 0; step < 15 && !graded; step++) {
      for (const gradeSel of ['button:has-text("Finish review")', 'button:has-text("Got it")']) {
        const grade = page.locator(gradeSel).first()
        if ((await grade.isVisible().catch(() => false)) && (await grade.isEnabled().catch(() => false))) {
          await grade.click()
          await page.getByText(/Scheduled next:/).first().waitFor({ timeout: 15000 })
          graded = true
          break
        }
      }
      if (graded) break
      let acted = false
      for (const sel of ['button:has-text("Flip card")', 'button:has-text("Next question")', 'button:has-text("Next card")']) {
        const el = page.locator(sel).first()
        if (await el.isVisible().catch(() => false)) {
          await el.click()
          acted = true
          break
        }
      }
      if (!acted) {
        const mcqChoice = page.locator('button', { hasText: /^A\./ }).first()
        if (await mcqChoice.isVisible().catch(() => false)) {
          await mcqChoice.click()
          acted = true
        }
      }
      if (!acted) {
        const ta = page.locator('textarea').first()
        if (await ta.isVisible().catch(() => false)) {
          await ta.fill('early recall attempt')
          await page.getByRole('button', { name: 'Reveal' }).click()
          acted = true
        }
      }
      if (!acted) await page.waitForTimeout(400)
    }
    check('early review graded successfully', graded)
  }

  await page.goto(`${BASE}/app/sessions/${session.id}`)
  await page.getByRole('button', { name: /Learn this chat/ }).click()
  await page.getByText('Learning artifacts').waitFor({ timeout: 120000 })
  await page.screenshot({ path: 'e2e/shots/features-learn.png', fullPage: true })
} catch (err) {
  check('features check crashed', false, String(err).slice(0, 300))
  await page.screenshot({ path: 'e2e/shots/features-fail.png', fullPage: true })
} finally {
  console.log(results.join('\n'))
  await browser.close()
}
