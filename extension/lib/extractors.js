/**
 * Pure conversation extractors — platform API JSON in, Trivium messages out.
 * No DOM, no fetch: fully unit-testable in Node.
 */

/** Claude: /api/organizations/{org}/chat_conversations/{id}?rendering_mode=messages */
export function parseClaudeConversation(data) {
  const messages = []
  for (const msg of data?.chat_messages ?? []) {
    const role = msg.sender === 'human' ? 'user' : msg.sender === 'assistant' ? 'assistant' : null
    if (!role) continue
    const parts = []
    for (const block of msg.content ?? []) {
      if (typeof block?.text === 'string' && block.text.trim()) parts.push(block.text)
      // tool results / thinking blocks are skipped; code the user saw lives in text blocks
    }
    for (const att of msg.attachments ?? []) {
      if (att?.extracted_content) parts.push(`[attachment: ${att.file_name ?? 'file'}]\n${att.extracted_content}`)
    }
    const content = parts.join('\n\n').trim()
    if (!content) continue
    messages.push({
      role,
      content: content.slice(0, 100_000),
      authored_by: role === 'assistant' ? 'ai' : 'user',
      timestamp: msg.created_at ?? null,
    })
  }
  return { title: (data?.name || '').slice(0, 300) || null, messages }
}

/** ChatGPT: /backend-api/conversation/{id} (also share payloads with a mapping). */
export function parseChatGPTConversation(data) {
  const mapping = data?.mapping
  if (!mapping || typeof mapping !== 'object') return { title: null, messages: [] }

  // Walk the active branch: from current_node up via parents, then reverse.
  const chain = []
  let nodeId = data.current_node ?? null
  const visited = new Set()
  while (nodeId && mapping[nodeId] && !visited.has(nodeId)) {
    visited.add(nodeId)
    chain.push(mapping[nodeId])
    nodeId = mapping[nodeId].parent
  }
  chain.reverse()
  // Fallback when current_node is absent: chronological order.
  const nodes = chain.length
    ? chain
    : Object.values(mapping).sort((a, b) => (a.message?.create_time ?? 0) - (b.message?.create_time ?? 0))

  const messages = []
  for (const node of nodes) {
    const msg = node?.message
    if (!msg) continue
    const role = msg.author?.role
    if (role !== 'user' && role !== 'assistant') continue
    if (msg.metadata?.is_visually_hidden_from_conversation) continue
    const content = extractChatGPTContent(msg.content)
    if (!content) continue
    messages.push({
      role,
      content: content.slice(0, 100_000),
      authored_by: role === 'assistant' ? 'ai' : 'user',
      timestamp: msg.create_time ? new Date(msg.create_time * 1000).toISOString() : null,
    })
  }
  return { title: (data?.title || '').slice(0, 300) || null, messages }
}

function extractChatGPTContent(content) {
  if (!content) return ''
  if (content.content_type === 'text' || content.content_type === 'multimodal_text') {
    return (content.parts ?? [])
      .map((p) => {
        if (typeof p === 'string') return p
        if (p?.content_type === 'audio_transcription') return p.text ?? ''
        return ''
      })
      .join('\n')
      .trim()
  }
  if (content.content_type === 'code') return content.text ? '```\n' + content.text + '\n```' : ''
  return ''
}

/** Identify the platform + conversation id from a browser tab URL. */
export function detectChatPage(url) {
  let parsed
  try {
    parsed = new URL(url)
  } catch {
    return null
  }
  const host = parsed.hostname
  if (host === 'claude.ai') {
    const m = parsed.pathname.match(/^\/chat\/([0-9a-f-]{36})/i)
    if (m) return { platform: 'claude', conversationId: m[1] }
  }
  if (host === 'chatgpt.com' || host === 'chat.openai.com') {
    const m = parsed.pathname.match(/^\/(?:c|share)\/([0-9a-zA-Z-]+)/)
    if (m) return { platform: 'chatgpt', conversationId: m[1], isShare: parsed.pathname.startsWith('/share/') }
  }
  return null
}
