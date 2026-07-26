/**
 * Loads the extension in real Chromium and exercises the popup against the
 * local backend (must be running on :8000 with seeded demo user).
 * Run from frontend/ (where playwright is installed):  node ../extension/test/load.test.mjs
 */
import { fileURLToPath } from 'node:url'
import path from 'node:path'
import { mkdtempSync } from 'node:fs'
import os from 'node:os'
import { createRequire } from 'node:module'

// Resolve playwright from the invoking directory (run this from frontend/).
const require = createRequire(path.join(process.cwd(), 'package.json'))
const { chromium } = require('playwright')

const extPath = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const results = []
const check = (name, ok, extra = '') => {
  results.push(`${ok ? 'PASS' : 'FAIL'}  ${name}${extra ? ' — ' + extra : ''}`)
  if (!ok) process.exitCode = 1
}

const context = await chromium.launchPersistentContext(mkdtempSync(path.join(os.tmpdir(), 'trivium-ext-')), {
  channel: 'chromium',
  headless: true,
  args: [`--disable-extensions-except=${extPath}`, `--load-extension=${extPath}`],
})

try {
  // Service worker must register without syntax errors.
  let [worker] = context.serviceWorkers()
  if (!worker) worker = await context.waitForEvent('serviceworker', { timeout: 15000 })
  check('service worker registered', Boolean(worker), worker?.url())
  const extensionId = new URL(worker.url()).hostname

  // Popup renders.
  const page = await context.newPage()
  await page.goto(`chrome-extension://${extensionId}/popup.html`)
  await page.waitForSelector('#view-login', { state: 'visible', timeout: 10000 })
  check('popup shows login view', true)

  // Live login against local backend with the seeded demo user.
  await page.fill('#apiUrl', 'http://localhost:8000')
  await page.fill('#email', 'demo@trivium.dev')
  await page.fill('#password', 'Demo1234!')
  await page.click('#loginBtn')
  await page.waitForSelector('#view-app', { state: 'visible', timeout: 15000 })
  check('login via background worker succeeds', true)
  check('email shown', (await page.textContent('#who'))?.includes('demo@trivium.dev') ?? false)

  const options = await page.locator('#project option').allTextContents()
  check('projects loaded from Trivium API', options.length >= 3, options.join(' | '))

  const info = await page.textContent('#pageInfo')
  check('non-chat tab handled gracefully', info?.includes('Open a ChatGPT') ?? false)

  // Logged-out state after logout.
  await page.click('#logoutBtn')
  await page.waitForSelector('#view-login', { state: 'visible', timeout: 10000 })
  check('logout returns to login view', true)
} catch (err) {
  check('extension test crashed', false, String(err).slice(0, 300))
} finally {
  console.log(results.join('\n'))
  await context.close()
}
