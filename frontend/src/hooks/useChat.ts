import { useCallback, useRef, useState } from 'react'

import { getConversation, streamChat } from '../services/api'
import type { ChatMessage } from '../types/chat'

interface Options {
  /** Appelé à la fin de chaque réponse (pour rafraîchir la liste des conversations). */
  onReplyDone?: () => void
}

export function useChat({ onReplyDone }: Options = {}) {
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const abortRef = useRef<AbortController | null>(null)
  // Incrémenté à chaque changement de conversation : les réponses tardives
  // d'une conversation quittée sont ignorées.
  const sessionRef = useRef(0)

  const switchTo = useCallback((id: string | null) => {
    abortRef.current?.abort()
    abortRef.current = null
    sessionRef.current += 1
    setConversationId(id)
    setMessages([])
    setIsStreaming(false)
    return sessionRef.current
  }, [])

  const open = useCallback(
    async (id: string) => {
      const session = switchTo(id)
      setIsLoading(true)
      try {
        const detail = await getConversation(id)
        if (session !== sessionRef.current) return
        setMessages(detail.messages.map(({ role, content }) => ({ role, content })))
      } catch {
        if (session !== sessionRef.current) return
        setMessages([
          { role: 'assistant', content: '⚠️ Impossible de charger cette conversation.' },
        ])
      } finally {
        if (session === sessionRef.current) setIsLoading(false)
      }
    },
    [switchTo],
  )

  const reset = useCallback(() => {
    switchTo(null)
    setIsLoading(false)
  }, [switchTo])

  const send = useCallback(
    async (content: string) => {
      const session = sessionRef.current
      const isCurrent = () => session === sessionRef.current

      // La question + une réponse vide qui se remplira au fil du streaming.
      setMessages((prev) => [
        ...prev,
        { role: 'user', content },
        { role: 'assistant', content: '' },
      ])
      setIsStreaming(true)

      const appendToLast = (text: string) => {
        if (!isCurrent()) return
        setMessages((prev) => {
          const last = prev[prev.length - 1]
          return [...prev.slice(0, -1), { ...last, content: last.content + text }]
        })
      }

      const controller = new AbortController()
      abortRef.current = controller
      try {
        await streamChat(
          { conversationId, message: content },
          {
            onConversationId: (id) => isCurrent() && setConversationId(id),
            onChunk: appendToLast,
          },
          controller.signal,
        )
      } catch (err) {
        if (!controller.signal.aborted) {
          appendToLast(`⚠️ ${err instanceof Error ? err.message : 'Erreur inconnue'}`)
        }
      } finally {
        if (isCurrent()) {
          // Réponse interrompue avant le premier mot : on retire la bulle vide.
          setMessages((prev) => {
            const last = prev[prev.length - 1]
            return last?.role === 'assistant' && !last.content ? prev.slice(0, -1) : prev
          })
          setIsStreaming(false)
          abortRef.current = null
        }
        onReplyDone?.()
      }
    },
    [conversationId, onReplyDone],
  )

  const stop = useCallback(() => abortRef.current?.abort(), [])

  return { conversationId, messages, isStreaming, isLoading, send, stop, open, reset }
}
