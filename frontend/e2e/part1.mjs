/** Trivium E2E part 1: landing -> signup -> project -> import -> extraction -> Learn recall flow. */
import { chromium } from 'playwright'
import { writeFileSync } from 'node:fs'

const BASE = 'http://localhost:4173'
const email = `e2e-${Date.now()}@test.dev`
const password = 'E2eStrong123'
const results = []
const check = (name, ok, extra = '') => {
  results.push(`${ok ? 'PASS' : 'FAIL'}  ${name}${extra ? ' — ' + extra : ''}`)
  if (!ok) process.exitCode = 1
}

const TRANSCRIPT = `User: I need to add JWT authentication to my FastAPI backend. Should I use sessions instead?
Assistant: We decided on JWT instead of server-side sessions because your SPA and API live on different origins. The tradeoff: revocation requires a refresh token table. Here's the flow with PyJWT...
User: I'm getting an error - InvalidSignatureError when verifying the jwt token.
Assistant: That bug means the signing secret differs from the verifying secret. The fix is loading SECRET_KEY from a single config source. Classic config-drift issue in fastapi middleware architecture.
User: Fixed it! Also added bcrypt hashing, same pattern as before in my last project.
Assistant: Good - recurring pattern: authentication hardening across your service layer, component architecture and middleware pipeline with bcrypt plus jwt plus rate limit protection.`

const browser = await chromium.launch()
const page = await browser.newPage()
page.setDefaultTimeout(20000)
const nav = (name) => page.locator('aside nav').getByRole('link', { name })

try {
  // Landing
  await page.goto(BASE)
  await page.getByText('getting dumber.').waitFor()
  check('landing shows positioning', true)
  check('landing science table', await page.getByText('Roediger & Karpicke').isVisible())

  // Signup
  await page.getByRole('link', { name: 'Get started' }).click()
  await page.getByPlaceholder('Display name (optional)').fill('E2E Tester')
  await page.getByPlaceholder('you@example.com').fill(email)
  await page.getByPlaceholder(/Password/).fill(password)
  await page.getByRole('button', { name: 'Sign up' }).click()
  await page.waitForURL('**/app')
  await page.getByText('Welcome back, E2E Tester').waitFor()
  check('signup lands on dashboard', true)

  // Create project
  await nav('Projects').click()
  await page.getByPlaceholder('New project name').fill('E2E Auth Service')
  await page.getByRole('button', { name: 'Create' }).click()
  await page.waitForSelector('text=E2E Auth Service')
  check('project created', true)

  // Import session
  await nav('Sessions').click()
  await page.getByRole('link', { name: '+ Import a session' }).click()
  await page.locator('select').nth(1).selectOption({ label: 'E2E Auth Service' })
  await page.getByPlaceholder(/Debugging the auth middleware/).fill('E2E JWT session')
  await page.locator('textarea').fill(TRANSCRIPT)
  await page.getByText(/Parsed 6 messages/).waitFor()
  check('transcript parsed', true)
  await page.getByRole('button', { name: 'Import session' }).click()
  await page.waitForURL(/\/app\/sessions\/[0-9a-f-]+$/)

  // Session detail: extraction result
  await page.getByText('Extracted knowledge').waitFor()
  await page.reload() // extraction runs in background right after import; reload for final status
  await page.getByText('Extracted knowledge').waitFor()
  check('extraction completed badge', await page.getByText('completed', { exact: true }).first().isVisible())
  check('wrapped fidelity shown honestly', await page.getByText('wrapped', { exact: true }).first().isVisible())
  const unitsCard = page.locator('div.card', { hasText: 'Extracted knowledge' })
  const unitCount = await unitsCard.locator('li').count()
  check('knowledge units listed', unitCount >= 2, `${unitCount} units`)

  // Learn this chat
  await page.getByRole('button', { name: /Learn this chat/ }).click()
  await page.getByText('Learning artifacts').waitFor({ timeout: 30000 })
  check('learn artifacts generated', await page.getByText(/Covering \d+ knowledge unit/).isVisible())

  // Recall flow: reveal disabled until an attempt is written (testing effect)
  const firstReveal = page.getByRole('button', { name: 'Write your attempt first' }).first()
  check('reveal gated on attempt (testing effect)', await firstReveal.isDisabled())
  await page.locator('textarea').first().fill('My recall attempt: we chose JWT because the SPA and API are on different origins.')
  await page.getByRole('button', { name: 'Reveal' }).first().click()
  check('reveal after attempt works', true)

  // Learn page: time-range scope
  await nav('Learn').click()
  await page.getByRole('button', { name: /A time range/ }).click()
  await page.locator('input[type=date]').first().fill('2020-01-01')
  await page.locator('input[type=date]').nth(1).fill('2030-01-01')
  await page.getByRole('button', { name: /Generate learning artifacts/ }).click()
  await page.getByText(/artifacts? covering \d+ knowledge units/).waitFor({ timeout: 30000 })
  check('time-range learn works', true)

  // Review queue: diffuse-mode delay means nothing due yet
  await nav('Review').click()
  await page.getByText(/Nothing due for review/).waitFor()
  check('diffuse delay: nothing reviewable immediately', await page.getByText(/Next review unlocks/).isVisible())

  writeFileSync('e2e/e2e-state.json', JSON.stringify({ email, password }))
} catch (err) {
  check('part1 crashed', false, String(err).slice(0, 400))
  await page.screenshot({ path: 'e2e/e2e-fail-part1.png' })
} finally {
  console.log(results.join('\n'))
  await browser.close()
}
