import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { fetchMe, login as apiLogin, register as apiRegister } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [businesses, setBusinesses] = useState([])
  const [activeBusinessId, setActiveBusinessId] = useState(
    () => localStorage.getItem('sf_business_id') || null
  )
  const [loading, setLoading] = useState(true)

  const applyAuth = useCallback((token, userData, bizList) => {
    if (token) localStorage.setItem('sf_token', token)
    setUser(userData)
    const list = bizList || []
    setBusinesses(list)
    if (list.length) {
      const preferred =
        list.find((b) => b.id === localStorage.getItem('sf_business_id')) || list[0]
      setActiveBusinessId(preferred.id)
      localStorage.setItem('sf_business_id', preferred.id)
    }
  }, [])

  const refresh = useCallback(async () => {
    const token = localStorage.getItem('sf_token')
    if (!token) {
      setUser(null)
      setBusinesses([])
      setLoading(false)
      return
    }
    try {
      const data = await fetchMe()
      applyAuth(token, data.user, data.businesses)
    } catch {
      localStorage.removeItem('sf_token')
      setUser(null)
      setBusinesses([])
    } finally {
      setLoading(false)
    }
  }, [applyAuth])

  useEffect(() => {
    refresh()
  }, [refresh])

  const login = async (email, password) => {
    const data = await apiLogin({ email, password })
    applyAuth(data.token, data.user, data.businesses)
    return data
  }

  const register = async (payload) => {
    const data = await apiRegister(payload)
    const bizList = data.business ? [data.business] : []
    applyAuth(data.token, data.user, bizList)
    return data
  }

  const logout = () => {
    localStorage.removeItem('sf_token')
    localStorage.removeItem('sf_business_id')
    setUser(null)
    setBusinesses([])
    setActiveBusinessId(null)
  }

  const selectBusiness = (id) => {
    setActiveBusinessId(id)
    localStorage.setItem('sf_business_id', id)
  }

  const upsertBusiness = (biz) => {
    setBusinesses((prev) => {
      const idx = prev.findIndex((b) => b.id === biz.id)
      if (idx === -1) return [biz, ...prev]
      const next = [...prev]
      next[idx] = biz
      return next
    })
  }

  const activeBusiness = businesses.find((b) => b.id === activeBusinessId) || null

  return (
    <AuthContext.Provider
      value={{
        user,
        businesses,
        activeBusiness,
        activeBusinessId,
        loading,
        login,
        register,
        logout,
        refresh,
        selectBusiness,
        upsertBusiness,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
