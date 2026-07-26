/** Capture screenshots of key pages with the seeded demo user for visual review. */
import { chromium } from 'playwright'

const BASE = 'http://localhost:4173'
const OUT = 'e2e/shots'
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 950 } })
page.setDefaultTimeout(20000)

await page.goto(`${BASE}/login`)
await page.getByPlaceholder('you@example.com').fill('demo@trivium.dev')
await page.getByPlaceholder('Password').fill('Demo1234!')
await page.getByRole('button', { name: 'Log in' }).click()
await page.waitForURL('**/app')
await page.waitForTimeout(1200)

const shots = [
  ['/', 'landing', 'networkidle'],
  ['/app', 'dashboard'],
  ['/app/metrics', 'metrics'],
  ['/app/review', 'review'],
  ['/app/profile', 'profile'],
]
for (const [path, name, wait] of shots) {
  await page.goto(`${BASE}${path}`, { waitUntil: wait ?? 'load' })
  await page.waitForTimeout(1500)
  await page.screenshot({ path: `${OUT}/${name}.png`, fullPage: name === 'landing' })
  console.log(`captured ${name}`)
}
await browser.close()
