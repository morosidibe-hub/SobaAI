import type { Conversation, ConversationDetail, User } from '../types/chat'

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

// Appelé quand le backend répond 401 (session expirée…) : l'app revient à l'écran de connexion.
let onUnauthorized: (() => void) | null = null
export function setUnauthorizedHandler(handler: (() => void) | null) {
  onUnauthorized = handler
}

async function ensureOk(response: Response): Promise<void> {
  if (response.ok) return
  let message = `Erreur serveur (${response.status})`
  try {
    const body = await response.json()
    if (typeof body.detail === 'string') message = body.detail
    else if (response.status === 422) message = 'Données invalides'
  } catch {
    // corps non JSON : on garde le message générique
  }
  if (response.status === 401) onUnauthorized?.()
  throw new ApiError(response.status, message)
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init)
  await ensureOk(response)
  return (response.status === 204 ? undefined : await response.json()) as T
}

const postJson = <T>(url: string, body?: unknown) =>
  request<T>(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })

// --- Authentification (la session est un cookie httpOnly géré par le navigateur) ---

export const getMe = () => request<User>('/api/auth/me')
export const login = (email: string, password: string) =>
  postJson<User>('/api/auth/login', { email, password })
export const register = (email: string, password: string) =>
  postJson<User>('/api/auth/register', { email, password })
export const logout = () => postJson<void>('/api/auth/logout')

// --- Conversations ---

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
  await ensureOk(response)
  if (!response.body) throw new Error('Réponse vide du serveur')

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
