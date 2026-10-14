import type { Conversation, ConversationDetail } from '../types/chat'

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init)
  if (!response.ok) throw new Error(`Erreur serveur (${response.status})`)
  return (response.status === 204 ? undefined : await response.json()) as T
}

export const listConversations = () => request<Conversation[]>('/api/conversations')

export const getConversation = (id: string) =>
  request<ConversationDetail>(`/api/conversations/${id}`)

export const deleteConversation = (id: string) =>
  request<void>(`/api/conversations/${id}`, { method: 'DELETE' })

/**
 * Envoie un message et appelle `onChunk` à chaque morceau de texte reçu.
 * Sans `conversationId`, le backend crée une conversation : son id est passé à
 * `onConversationId` dès réception des en-têtes, avant le début du texte.
 */
export async function streamChat(
  params: { conversationId: string | null; message: string },
  handlers: { onConversationId: (id: string) => void; onChunk: (text: string) => void },
  signal?: AbortSignal,
): Promise<void> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ conversation_id: params.conversationId, message: params.message }),
    signal,
  })

  if (!response.ok || !response.body) {
    throw new Error(`Erreur serveur (${response.status})`)
  }

  const id = response.headers.get('X-Conversation-Id')
  if (id) handlers.onConversationId(id)

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  for (;;) {
    const { done, value } = await reader.read()
    if (done) break
    handlers.onChunk(decoder.decode(value, { stream: true }))
  }
}
