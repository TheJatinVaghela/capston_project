import { useState, useEffect } from 'react'

export function useSession(storageKey = 'sf_session_id') {
  const [sessionId, setSessionIdState] = useState('')

  useEffect(() => {
    let id = localStorage.getItem(storageKey)
    if (!id) {
      id = crypto.randomUUID()
      localStorage.setItem(storageKey, id)
    }
    setSessionIdState(id)
  }, [storageKey])

  const resetSession = () => {
    const id = crypto.randomUUID()
    localStorage.setItem(storageKey, id)
    setSessionIdState(id)
    return id
  }

  const loadSession = (id) => {
    if (!id) return
    localStorage.setItem(storageKey, id)
    setSessionIdState(id)
  }

  return { sessionId, resetSession, loadSession }
}
