/** Full production walkthrough against the LIVE deployment. */
import { chromium } from 'playwright'

const BASE = process.env.BASE_URL || 'https://trivium-dun.vercel.app'
const email = `prod-${Date.now()}@trivium.dev`
const password = 'ProdCheck123'
const results = []
const check = (name, ok, extra = '') => {
  results.push(`${ok ? 'PASS' : 'FAIL'}  ${name}${extra ? ' — ' + extra : ''}`)
  if (!ok) process.exitCode = 1
}

const TRANSCRIPT = `User: I need to add JWT authentication to my FastAPI backend. Should I use sessions instead?
Assistant: We decided on JWT instead of server-side sessions because your SPA and API live on different origins. The tradeoff: revocation requires a refresh token table.
User: I'm getting an error - InvalidSignatureError when verifying the jwt token.
Assistant: That bug means the signing secret differs from the verifying secret. The fix is loading SECRET_KEY from a single config source. Classic config-drift issue in fastapi middleware architecture.
User: Fixed it! Also added bcrypt hashing, same pattern as before in my last project.
Assistant: Good - recurring pattern: authentication hardening across your service layer, component architecture and middleware pipeline.`

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } })
page.setDefaultTimeout(60000) // free tier can be slow on cold paths
const nav = (name) => page.locator('aside nav').getByRole('link', { name })

try {
  // Landing + signup
  await page.goto(BASE)
  await page.getByText('getting dumber.').waitFor()
  check('landing loads', true)
  await page.getByRole('link', { name: 'Get started' }).click()
  await page.getByPlaceholder('you@example.com').fill(email)
  await page.getByPlaceholder(/Password/).fill(password)
  await page.getByRole('button', { name: 'Sign up' }).click()
  await page.waitForURL('**/app', { timeout: 90000 })
  check('signup -> dashboard (CORS + auth working)', true)

  // Import session
  await nav('Sessions').click()
  await page.getByRole('link', { name: '+ Import a session' }).click()
  await page.getByPlaceholder(/Debugging the auth middleware/).fill('Prod check session')
  await page.locator('textarea').fill(TRANSCRIPT)
  await page.getByText(/Parsed 6 messages/).waitFor()
  await page.getByRole('button', { name: 'Import session' }).click()
  await page.waitForURL(/\/app\/sessions\/[0-9a-f-]+$/)
  await page.waitForTimeout(4000) // background extraction on the live server
  await page.reload()
  await page.getByText('Extracted knowledge').waitFor()
  const unitsCard = page.locator('div.card', { hasText: 'Extracted knowledge' })
  const unitCount = await unitsCard.locator('li').count()
  check('extraction produced units in production', unitCount >= 2, `${unitCount} units`)

  // Learn
  await page.getByRole('button', { name: /Learn this chat/ }).click()
  await page.getByText('Learning artifacts').waitFor({ timeout: 90000 })
  check('learn generates artifacts', true)

  // Early review with a grade
  await page.goto(`${BASE}/app/review?early=1`)
  await page.getByText(/1 of \d+/).waitFor()
  check('early review queue loads', true)
  let graded = false
  for (let step = 0; step < 20 && !graded; step++) {
    for (const sel of ['button:has-text("Finish review")', 'button:has-text("Got it")']) {
      const b = page.locator(sel).first()
      if ((await b.isVisible().catch(() => false)) && (await b.isEnabled().catch(() => false))) {
        await b.click()
        await page.getByText(/Scheduled next:/).first().waitFor({ timeout: 30000 })
        graded = true
        break
      }
    }
    if (graded) break
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
      const mcq = page.locator('button', { hasText: /^A\./ }).first()
      if (await mcq.isVisible().catch(() => false)) {
        await mcq.click()
        acted = true
      }
    }
    if (!acted) {
      const ta = page.locator('textarea').first()
      if ((await ta.isVisible().catch(() => false)) && (await ta.isEnabled().catch(() => false))) {
        await ta.fill('the signing secret differed from the verifying secret; load SECRET_KEY from one config source')
        const reveal = page.getByRole('button', { name: 'Reveal' })
        if (await reveal.isVisible().catch(() => false)) await reveal.click()
        acted = true
      }
    }
    if (!acted) await page.waitForTimeout(500)
  }
  check('review graded in production', graded)

  // Profile + metrics + skills render
  await nav('Profile').click()
  await page.getByText('Knowledge Profile').first().waitFor()
  check('profile renders', true)
  await nav('Metrics').click()
  await page.getByText('Retention curve').waitFor()
  check('metrics renders', true)
  await nav('Improve').click()
  await page.getByText('Language report').waitFor()
  check('skills page renders', true)

  await page.screenshot({ path: 'e2e/shots/prod-live.png' })

  // Logout
  await page.getByRole('button', { name: 'Log out' }).click()
  await page.waitForURL(BASE + '/**')
  check('logout works', true)
} catch (err) {
  check('prod check crashed', false, String(err).slice(0, 300))
  await page.screenshot({ path: 'e2e/shots/prod-fail.png', fullPage: true })
} finally {
  console.log(results.join('\n'))
  await browser.close()
}
