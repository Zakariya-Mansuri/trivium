/** Node unit tests for the pure extractors. Run: node --test extension/test/ */
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { detectChatPage, parseChatGPTConversation, parseClaudeConversation } from '../lib/extractors.js'

// --- Claude fixture: shape of /chat_conversations/{id}?rendering_mode=messages ---
const claudeFixture = {
  uuid: 'abc',
  name: 'Debugging FastAPI auth',
  chat_messages: [
    {
      sender: 'human',
      created_at: '2026-07-20T10:00:00Z',
      content: [{ type: 'text', text: 'Why does my JWT verification fail?' }],
      attachments: [],
    },
    {
      sender: 'assistant',
      created_at: '2026-07-20T10:00:30Z',
      content: [
        { type: 'text', text: 'Your signing secret differs from the verifying secret.' },
        { type: 'tool_use', text: '' },
        { type: 'text', text: '```python\njwt.decode(token, SECRET)\n```' },
      ],
      attachments: [],
    },
    {
      sender: 'human',
      created_at: '2026-07-20T10:01:00Z',
      content: [{ type: 'text', text: 'Here is my config file' }],
      attachments: [{ file_name: 'config.py', extracted_content: 'SECRET_KEY = "abc"' }],
    },
    { sender: 'assistant', created_at: '2026-07-20T10:01:30Z', content: [{ type: 'thinking', text: '' }], attachments: [] },
  ],
}

test('claude: extracts ordered messages with roles and authorship', () => {
  const { title, messages } = parseClaudeConversation(claudeFixture)
  assert.equal(title, 'Debugging FastAPI auth')
  assert.equal(messages.length, 3) // empty assistant message dropped
  assert.deepEqual(
    messages.map((m) => m.role),
    ['user', 'assistant', 'user'],
  )
  assert.equal(messages[0].authored_by, 'user')
  assert.equal(messages[1].authored_by, 'ai')
  assert.ok(messages[1].content.includes('jwt.decode'))
  assert.ok(messages[2].content.includes('[attachment: config.py]'))
  assert.ok(messages[2].content.includes('SECRET_KEY'))
})

test('claude: empty/garbage input yields no messages', () => {
  assert.deepEqual(parseClaudeConversation({}).messages, [])
  assert.deepEqual(parseClaudeConversation(null).messages, [])
})

// --- ChatGPT fixture: shape of /backend-api/conversation/{id} ---
const gptFixture = {
  title: 'React state help',
  current_node: 'n3',
  mapping: {
    root: { id: 'root', parent: null, children: ['n0'] },
    n0: {
      id: 'n0',
      parent: 'root',
      children: ['n1'],
      message: { author: { role: 'system' }, content: { content_type: 'text', parts: ['system stuff'] }, create_time: 1 },
    },
    n1: {
      id: 'n1',
      parent: 'n0',
      children: ['n2'],
      message: { author: { role: 'user' }, content: { content_type: 'text', parts: ['My React state is messy'] }, create_time: 2 },
    },
    n2: {
      id: 'n2',
      parent: 'n1',
      children: ['n3'],
      message: {
        author: { role: 'assistant' },
        content: { content_type: 'text', parts: ['Use a reducer with context.'] },
        create_time: 3,
      },
    },
    n3: {
      id: 'n3',
      parent: 'n2',
      children: [],
      message: {
        author: { role: 'user' },
        content: { content_type: 'multimodal_text', parts: ['Thanks!', { content_type: 'image_asset_pointer' }] },
        create_time: 4,
      },
    },
  },
}

test('chatgpt: walks the active branch in order, skips system', () => {
  const { title, messages } = parseChatGPTConversation(gptFixture)
  assert.equal(title, 'React state help')
  assert.deepEqual(
    messages.map((m) => m.role),
    ['user', 'assistant', 'user'],
  )
  assert.equal(messages[0].content, 'My React state is messy')
  assert.equal(messages[1].authored_by, 'ai')
  assert.equal(messages[2].content, 'Thanks!') // image part dropped, text kept
})

test('chatgpt: falls back to chronological order without current_node', () => {
  const noCurrent = { ...gptFixture, current_node: undefined }
  const { messages } = parseChatGPTConversation(noCurrent)
  assert.deepEqual(
    messages.map((m) => m.content),
    ['My React state is messy', 'Use a reducer with context.', 'Thanks!'],
  )
})

test('chatgpt: code content becomes a fenced block', () => {
  const data = {
    current_node: 'a',
    mapping: {
      a: {
        id: 'a',
        parent: null,
        message: { author: { role: 'assistant' }, content: { content_type: 'code', text: 'print(1)' }, create_time: 1 },
      },
    },
  }
  const { messages } = parseChatGPTConversation(data)
  assert.equal(messages[0].content, '```\nprint(1)\n```')
})

// --- URL detection ---
test('detectChatPage: identifies platforms and ids', () => {
  assert.deepEqual(detectChatPage('https://claude.ai/chat/06f2e73a-adf7-4023-bea3-6feca7b83b15'), {
    platform: 'claude',
    conversationId: '06f2e73a-adf7-4023-bea3-6feca7b83b15',
  })
  const gpt = detectChatPage('https://chatgpt.com/c/6a65f388-3f8c-83ee')
  assert.equal(gpt.platform, 'chatgpt')
  assert.equal(gpt.isShare, false)
  const share = detectChatPage('https://chatgpt.com/share/6a65f388-3f8c-83ee')
  assert.equal(share.isShare, true)
  assert.equal(detectChatPage('https://claude.ai/new'), null)
  assert.equal(detectChatPage('https://evil.example/chat/x'), null)
  assert.equal(detectChatPage('not a url'), null)
})
