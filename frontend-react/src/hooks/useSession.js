import { useState, useEffect } from 'react'

const SESSION_KEY = 'techflow_session_id'

export function useSession() {
  const [sessionId, setSessionId] = useState('')

  useEffect(() => {
    let id = localStorage.getItem(SESSION_KEY)
    if (!id) {
      id = crypto.randomUUID()
      localStorage.setItem(SESSION_KEY, id)
    }
    setSessionId(id)
  }, [])

  const resetSession = () => {
    const id = crypto.randomUUID()
    localStorage.setItem(SESSION_KEY, id)
    setSessionId(id)
    return id
  }

  return { sessionId, resetSession }
}
