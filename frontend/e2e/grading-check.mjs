/** Verify: AI-assisted grading with override UI + early queue no longer loops. */
import { chromium } from 'playwright'

const BASE = process.env.BASE_URL || 'http://localhost:4173'
const API = (process.env.API_URL || 'http://localhost:8001') + '/api/v1'
const email = `grade-${Date.now()}@test.dev`
const results = []
const check = (name, ok, extra = '') => {
  results.push(`${ok ? 'PASS' : 'FAIL'}  ${name}${extra ? ' — ' + extra : ''}`)
  if (!ok) process.exitCode = 1
}

const tokens = await (
  await fetch(`${API}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password: 'GradeCheck1', display_name: 'Grade Check' }),
  })
).json()
const auth = { 'Content-Type': 'application/json', Authorization: `Bearer ${tokens.access_token}` }
await fetch(`${API}/sessions/import`, {
  method: 'POST',
  headers: auth,
  body: JSON.stringify({
    source_tool: 'chatgpt',
    title: 'Grading check',
    messages: [
      { role: 'user', content: 'Why does my jwt verification fail with InvalidSignatureError?' },
      { role: 'assistant', content: 'That bug means the signing secret differs from the verifying secret. The fix is loading SECRET_KEY from a single config source in your fastapi middleware.' },
      { role: 'user', content: 'I decided to use bcrypt instead of argon2 for password hashing, tradeoff was maturity.' },
      { role: 'assistant', content: 'Reasonable decision — bcrypt is battle-tested. Same pattern as your last authentication project.' },
    ],
  }),
})

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } })
page.setDefaultTimeout(25000)

const gradeOne = async (attemptText) => {
  // Work the current item until graded; returns which grade path was used.
  for (let step = 0; step < 20; step++) {
    if (await page.getByText(/Queue cleared|Nothing due/).isVisible().catch(() => false)) return 'cleared'
    const suggested = page.locator('button', { hasText: 'AI suggests' }).first()
    if ((await suggested.isVisible().catch(() => false)) && (await suggested.isEnabled().catch(() => false))) {
      await suggested.click()
      await page.getByText(/Scheduled next:/).first().waitFor({ timeout: 15000 })
      return 'ai'
    }
    const finish = page.locator('button:has-text("Finish review")').first()
    if ((await finish.isVisible().catch(() => false)) && (await finish.isEnabled().catch(() => false))) {
      await finish.click()
      await page.getByText(/Scheduled next:/).first().waitFor({ timeout: 15000 })
      return 'mcq'
    }
    const gotIt = page.locator('button:has-text("Got it")').first()
    if ((await gotIt.isVisible().catch(() => false)) && (await gotIt.isEnabled().catch(() => false))) {
      await gotIt.click()
      await page.getByText(/Scheduled next:/).first().waitFor({ timeout: 15000 })
      return 'manual'
    }
    let acted = false
    for (const sel of ['button:has-text("Flip card")', 'button:has-text("Next card")', 'button:has-text("Next question")']) {
      const el = page.locator(sel).first()
      if (await el.isVisible().catch(() => false)) {
        await el.click()
        acted = true
        break
      }
    }
    if (!acted) {
      const ta = page.locator('textarea').first()
      if ((await ta.isVisible().catch(() => false)) && (await ta.isEnabled().catch(() => false))) {
        await ta.fill(attemptText)
        const reveal = page.getByRole('button', { name: 'Reveal' })
        if (await reveal.isVisible().catch(() => false)) {
          await reveal.click()
          acted = true
        }
      }
    }
    if (!acted) await page.waitForTimeout(400)
  }
  return 'stuck'
}

try {
  await page.goto(`${BASE}/login`)
  await page.getByPlaceholder('you@example.com').fill(email)
  await page.getByPlaceholder('Password').fill('GradeCheck1')
  await page.getByRole('button', { name: 'Log in' }).click()
  await page.waitForURL('**/app')

  await page.goto(`${BASE}/app/review?early=1`)
  await page.getByText(/1 of \d+/).waitFor()

  // Grade every item in the early queue; at least one should use the AI path.
  const paths = []
  let sawVerdictCard = false
  for (let i = 0; i < 12; i++) {
    await page.waitForTimeout(1200) // let queue reloads settle between items
    const cleared = await page.getByText(/Queue cleared|Nothing due/).isVisible().catch(() => false)
    if (cleared) break
    const hasItem = await page.getByText(/\d+ of \d+/).isVisible().catch(() => false)
    if (!hasItem) continue
    const path = await gradeOne('the signing secret differs from the verifying secret, load SECRET_KEY from one config source')
    paths.push(path)
    if (path === 'ai') sawVerdictCard = true
    if (path === 'stuck') break
  }
  check('graded items without getting stuck', paths.length > 0 && !paths.includes('stuck'), paths.join(','))
  check('AI verdict + override path exercised', sawVerdictCard)

  // Loop bug: after clearing, the queue must show DONE, not the same items again.
  await page.waitForTimeout(800)
  const cleared = await page.getByText(/Queue cleared|Nothing due/).isVisible().catch(() => false)
  const stillLooping = await page.getByText(/1 of \d+/).isVisible().catch(() => false)
  check('queue ends instead of looping', cleared && !stillLooping)
  await page.screenshot({ path: 'e2e/shots/grading-done.png' })
} catch (err) {
  check('grading check crashed', false, String(err).slice(0, 300))
  await page.screenshot({ path: 'e2e/shots/grading-fail.png', fullPage: true })
} finally {
  console.log(results.join('\n'))
  await browser.close()
}
