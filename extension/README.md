# ▲ Trivium Companion (browser extension)

One-click import of your **ChatGPT** and **Claude** conversations into Trivium — no copy-pasting,
no format wrangling. The extension runs inside your logged-in browser and reads the conversation
from the platform's own API (the same data the page itself loads), then sends it to your Trivium
server tagged with honest `wrapped` fidelity.

**Purely programmatic** — no LLM involved in extraction.

## Install (developer mode)

1. Open Chrome/Edge/Brave → `chrome://extensions`
2. Enable **Developer mode** (top-right)
3. Click **Load unpacked** → select this `extension/` folder

## Use

1. Click the ▲ icon → log in with your Trivium account
   (server defaults to `http://localhost:8000`; point it at your Render URL in production)
2. Open any conversation on `chatgpt.com/c/…` or `claude.ai/chat/…`
3. Click the ▲ icon → pick a project (optional) → **Import this chat**
4. Trivium extracts knowledge units in the background — open the app and hit **Learn**

## How it works

| Platform | Source of truth |
|---|---|
| Claude | `claude.ai/api/organizations/{org}/chat_conversations/{id}?rendering_mode=messages` — your browser session's cookies authenticate the request |
| ChatGPT | `chatgpt.com/api/auth/session` → access token → `backend-api/conversation/{id}` (also works for `/share/…` links while logged in) |

Messages keep correct `authored_by` tagging (`ai` for assistant turns, `user` for yours), which
feeds Trivium's independence metrics. Attachments' extracted text is included for Claude.

Your Trivium credentials are stored in `chrome.storage.local` only; conversations go only to the
Trivium server you configured. Nothing is sent anywhere else.

## Tests

```bash
node --test extension/test/extractors.test.mjs     # pure extractor units (fixtures)
# with backend running on :8000 (seeded), from frontend/:
node ../extension/test/load.test.mjs               # loads extension in Chromium, live popup flow
```
