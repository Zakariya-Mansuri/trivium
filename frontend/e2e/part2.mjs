/** Trivium E2E part 2 (after make_due.py): login -> review flow -> profile -> metrics -> logout. */
import { chromium } from 'playwright'
import { readFileSync } from 'node:fs'

const BASE = 'http://localhost:4173'
const { email, password } = JSON.parse(readFileSync('e2e/e2e-state.json', 'utf8'))
const results = []
const check = (name, ok, extra = '') => {
  results.push(`${ok ? 'PASS' : 'FAIL'}  ${name}${extra ? ' — ' + extra : ''}`)
  if (!ok) process.exitCode = 1
}

const browser = await chromium.launch()
const page = await browser.newPage()
page.setDefaultTimeout(20000)
const nav = (name) => page.locator('aside nav').getByRole('link', { name })

try {
  // Login
  await page.goto(`${BASE}/login`)
  await page.getByPlaceholder('you@example.com').fill(email)
  await page.getByPlaceholder('Password').fill(password)
  await page.getByRole('button', { name: 'Log in' }).click()
  await page.waitForURL('**/app')
  check('login works', true)

  // Dashboard shows due reviews
  await page.getByText(/concepts? ready for recall/).waitFor()
  check('dashboard surfaces due reviews', true)

  // Review flow
  await nav('Review').click()
  await page.getByText(/1 of \d+/).waitFor()
  check('review queue loaded with items', true)

  // Full recall interaction: attempt -> reveal -> grade
  await page.locator('textarea').first().fill('Recall: the JWT signing secret must match the verifying secret; config drift caused it.')
  await page.getByRole('button', { name: 'Reveal' }).click()
  // Walk through any multi-prompt artifact until grade buttons appear
  for (let i = 0; i < 10; i++) {
    if (await page.getByRole('button', { name: 'Got it' }).isVisible().catch(() => false)) break
    const next = page.getByRole('button', { name: /Next prompt/ })
    if (await next.isVisible().catch(() => false)) {
      await page.locator('textarea').first().fill('Another recall attempt with real content.')
      await next.click()
      const reveal = page.getByRole('button', { name: 'Reveal' })
      if (await reveal.isVisible().catch(() => false)) await reveal.click()
    } else {
      await page.waitForTimeout(300)
    }
  }
  await page.getByRole('button', { name: 'Got it' }).click()
  await page.getByText(/Scheduled next:/).waitFor()
  check('review graded, SM-2 schedule shown', true)

  // Grade one more as incorrect to exercise that path
  if (await page.getByText(/\d+ of \d+/).isVisible().catch(() => false)) {
    await page.locator('textarea').first().fill('I do not remember this one.')
    await page.getByRole('button', { name: 'Reveal' }).click()
    for (let i = 0; i < 10; i++) {
      if (await page.getByRole('button', { name: "Didn't recall" }).isVisible().catch(() => false)) break
      const next = page.getByRole('button', { name: /Next prompt/ })
      if (await next.isVisible().catch(() => false)) {
        await page.locator('textarea').first().fill('attempt')
        await next.click()
        const reveal = page.getByRole('button', { name: 'Reveal' })
        if (await reveal.isVisible().catch(() => false)) await reveal.click()
      } else {
        await page.waitForTimeout(300)
      }
    }
    await page.getByRole('button', { name: "Didn't recall" }).click()
    await page.getByText(/status/).first().waitFor()
    check('incorrect grading path works', true)
  }

  // Profile reflects evidence
  await nav('Profile').click()
  await page.getByText('Knowledge Profile').first().waitFor()
  await page.getByText('learning', { exact: true }).first().waitFor()
  check('profile shows learning status from evidence', true)

  // Toggle visibility on first entry
  await page.getByRole('button', { name: 'private' }).first().click()
  await page.getByRole('button', { name: 'shared' }).first().waitFor()
  check('visibility toggle works', true)

  // Export downloads skill.md
  const downloadPromise = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Export skill.md' }).click()
  const download = await downloadPromise
  check('skill.md export downloads', download.suggestedFilename() === 'skill.md')

  // Metrics render
  await nav('Metrics').click()
  await page.getByText('Retention curve').waitFor()
  check('metrics: retention chart card', true)
  check('metrics: recall rate tile', await page.getByText('Overall recall rate').isVisible())
  check('metrics: activity heatmap', await page.getByText('Review activity').isVisible())
  check('metrics: independence bar', await page.getByText(/Independence/).isVisible())
  const svgCount = await page.locator('svg[role=img]').count()
  check('charts rendered as SVG', svgCount >= 2, `${svgCount} svgs`)

  // Agent chat quick check
  await nav('Agent').click()
  await page.getByPlaceholder(/Ask the agent/).fill('How should I structure error handling in my fastapi middleware?')
  await page.getByRole('button', { name: 'Send' }).click()
  await page.getByText(/mock provider|approach/).first().waitFor({ timeout: 30000 })
  check('agent chat responds', true)

  // Logout
  await page.getByRole('button', { name: 'Log out' }).click()
  await page.waitForURL(BASE + '/')
  await page.goto(`${BASE}/app`)
  await page.waitForURL('**/login')
  check('logout + protected route redirect', true)
} catch (err) {
  check('part2 crashed', false, String(err).slice(0, 400))
  await page.screenshot({ path: 'e2e/e2e-fail-part2.png' })
} finally {
  console.log(results.join('\n'))
  await browser.close()
}
