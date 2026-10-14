import { useCallback, useEffect, useState } from 'react'

import { deleteConversation, listConversations } from '../services/api'
import type { Conversation } from '../types/chat'

export function useConversations() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    try {
      setConversations(await listConversations())
      setError(null)
    } catch {
      setError('Historique indisponible (base de données démarrée ?)')
    }
  }, [])

  const remove = useCallback(async (id: string) => {
    await deleteConversation(id)
    setConversations((prev) => prev.filter((c) => c.id !== id))
  }, [])

  useEffect(() => {
    // Chargement initial de la liste au montage.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void refresh()
  }, [refresh])

  return { conversations, error, refresh, remove }
}
