const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000'

function authHeaders() {
  const token = localStorage.getItem('sf_token')
  return token
    ? { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
    : { 'Content-Type': 'application/json' }
}

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { ...authHeaders(), ...(options.headers || {}) },
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.error || `HTTP ${response.status}`)
  }
  return data
}

export { API_URL, request, authHeaders }

export async function register(body) {
  return request('/auth/register', { method: 'POST', body: JSON.stringify(body) })
}

export async function login(body) {
  return request('/auth/login', { method: 'POST', body: JSON.stringify(body) })
}

export async function fetchMe() {
  return request('/auth/me')
}

export async function listBusinesses() {
  return request('/businesses')
}

export async function createBusiness(body) {
  return request('/businesses', { method: 'POST', body: JSON.stringify(body) })
}

export async function getBusiness(id) {
  return request(`/businesses/${id}`)
}

export async function updateBusiness(id, body) {
  return request(`/businesses/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export async function updateKnowledge(id, knowledgeOrText) {
  const body =
    typeof knowledgeOrText === 'string'
      ? { text: knowledgeOrText }
      : knowledgeOrText?.text != null
        ? { text: knowledgeOrText.text }
        : { knowledge: knowledgeOrText }
  return request(`/businesses/${id}/knowledge`, {
    method: 'PUT',
    body: JSON.stringify(body),
  })
}

export async function updateBusinessSettings(id, { ai_model, allowed_origins, chat_colors }) {
  const body = {}
  if (ai_model != null) body.ai_model = ai_model
  if (allowed_origins != null) body.allowed_origins = allowed_origins
  if (chat_colors != null) body.chat_colors = chat_colors
  return request(`/businesses/${id}/settings`, {
    method: 'PUT',
    body: JSON.stringify(body),
  })
}

export async function rotateWidgetKey(id) {
  return request(`/businesses/${id}/widget-key`, { method: 'POST', body: '{}' })
}

export async function getBillingConfig() {
  return request('/billing/config')
}

export async function createCheckout(businessId, plan = 'basic') {
  return request('/billing/checkout', {
    method: 'POST',
    body: JSON.stringify({ business_id: businessId, plan }),
  })
}

export async function openBillingPortal(businessId) {
  return request('/billing/portal', {
    method: 'POST',
    body: JSON.stringify({ business_id: businessId }),
  })
}

export async function confirmCheckout(businessId, sessionId) {
  return request('/billing/confirm', {
    method: 'POST',
    body: JSON.stringify({ business_id: businessId, session_id: sessionId }),
  })
}

export async function syncSubscription(businessId) {
  return request('/billing/sync', {
    method: 'POST',
    body: JSON.stringify({ business_id: businessId }),
  })
}

export async function sendChatMessage({
  message,
  model,
  useAi,
  sessionId,
  businessId,
  widgetKey,
  source,
}) {
  const body = {
    message,
    model,
    use_ai: useAi,
    session_id: sessionId,
    source: source || 'preview',
  }
  if (businessId) body.business_id = businessId
  if (widgetKey) body.widget_key = widgetKey

  const qs = widgetKey ? `?key=${encodeURIComponent(widgetKey)}` : ''
  const headers = {
    ...authHeaders(),
    ...(widgetKey ? { 'X-Widget-Key': widgetKey } : {}),
  }
  const response = await fetch(`${API_URL}/chat${qs}`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`)
  return data
}

/**
 * Stream chat tokens via SSE. Calls onToken(text) as pieces arrive,
 * returns the final done payload.
 */
export async function sendChatMessageStream({
  message,
  useAi,
  sessionId,
  businessId,
  widgetKey,
  source,
  onToken,
  onMeta,
}) {
  const body = {
    message,
    use_ai: useAi,
    session_id: sessionId,
    source: source || 'preview',
  }
  if (businessId) body.business_id = businessId
  if (widgetKey) body.widget_key = widgetKey

  const qs = widgetKey ? `?key=${encodeURIComponent(widgetKey)}` : ''
  const headers = {
    ...authHeaders(),
    ...(widgetKey ? { 'X-Widget-Key': widgetKey } : {}),
  }
  const response = await fetch(`${API_URL}/chat/stream${qs}`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.error || `HTTP ${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let donePayload = null

  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n\n')
    buffer = parts.pop() || ''
    for (const block of parts) {
      const line = block.trim()
      if (!line.startsWith('data:')) continue
      const jsonStr = line.replace(/^data:\s*/, '')
      let event
      try {
        event = JSON.parse(jsonStr)
      } catch {
        continue
      }
      if (event.type === 'token' && event.text) {
        onToken?.(event.text)
      } else if (event.type === 'meta') {
        onMeta?.(event)
      } else if (event.type === 'done') {
        donePayload = event
      } else if (event.type === 'error') {
        throw new Error(event.error || 'Stream error')
      }
    }
  }

  if (!donePayload) {
    throw new Error('Chat stream ended without a response')
  }
  return donePayload
}

export async function getSessionMessages(sessionId) {
  const response = await fetch(`${API_URL}/sessions/${sessionId}/messages`, {
    headers: authHeaders(),
  })
  if (!response.ok) return { messages: [] }
  return response.json()
}

export async function getStats(businessId) {
  if (!businessId) return null
  const qs = `?business_id=${encodeURIComponent(businessId)}`
  const response = await fetch(`${API_URL}/stats${qs}`, { headers: authHeaders() })
  if (!response.ok) return null
  return response.json()
}

export async function getModels() {
  const response = await fetch(`${API_URL}/models`)
  if (!response.ok) return { ollama_available: false }
  return response.json()
}

export async function clearLogs(businessId) {
  const qs = businessId ? `?business_id=${businessId}` : ''
  return request(`/logs${qs}`, { method: 'DELETE' })
}

export async function listSessions(businessId, limit = 40) {
  return request(`/businesses/${businessId}/sessions?limit=${limit}`)
}

export async function deleteSession(businessId, sessionId) {
  return request(`/businesses/${businessId}/sessions/${sessionId}`, {
    method: 'DELETE',
  })
}

export async function getPublicBusiness(slug) {
  return request(`/businesses/public/${slug}`)
}
