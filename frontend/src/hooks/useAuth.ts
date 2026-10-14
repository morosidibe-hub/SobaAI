import { useCallback, useEffect, useState } from 'react'

import * as api from '../services/api'
import type { User } from '../types/chat'

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    api.setUnauthorizedHandler(() => setUser(null))
    // Le cookie de session éventuel est envoyé automatiquement.
    api
      .getMe()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setIsLoading(false))
    return () => api.setUnauthorizedHandler(null)
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    setUser(await api.login(email, password))
  }, [])

  const register = useCallback(async (email: string, password: string) => {
    setUser(await api.register(email, password))
  }, [])

  const logout = useCallback(async () => {
    try {
      await api.logout()
    } finally {
      setUser(null)
    }
  }, [])

  return { user, isLoading, login, register, logout }
}
