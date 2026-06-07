const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000'

export async function sendChatMessage({ message, model, useAi, sessionId }) {
  const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      model,
      use_ai: useAi,
      session_id: sessionId,
    }),
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.error || `HTTP ${response.status}`)
  }

  return response.json()
}

export async function getSessionMessages(sessionId) {
  const response = await fetch(`${API_URL}/sessions/${sessionId}/messages`)
  if (!response.ok) return { messages: [] }
  return response.json()
}

export async function getStats() {
  const response = await fetch(`${API_URL}/stats`)
  if (!response.ok) return null
  return response.json()
}

export async function getModels() {
  const response = await fetch(`${API_URL}/models`)
  if (!response.ok) return { ollama_available: false }
  return response.json()
}

export async function clearLogs() {
  const response = await fetch(`${API_URL}/logs`, { method: 'DELETE' })
  return response.json()
}
