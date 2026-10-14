import { useState } from 'react'

import { useChat } from '../hooks/useChat'
import { useConversations } from '../hooks/useConversations'
import type { User } from '../types/chat'
import { ChatInput } from './ChatInput'
import { ChatWindow } from './ChatWindow'
import { Sidebar } from './Sidebar'

interface Props {
  user: User
  onLogout: () => void
}

export function ChatApp({ user, onLogout }: Props) {
  const { conversations, error, refresh, remove } = useConversations()
  const chat = useChat({ onReplyDone: refresh })
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const select = (id: string) => {
    setSidebarOpen(false)
    if (id !== chat.conversationId) void chat.open(id)
  }

  const startNew = () => {
    setSidebarOpen(false)
    chat.reset()
  }

  const removeConversation = async (id: string) => {
    if (!window.confirm('Supprimer cette conversation ?')) return
    try {
      await remove(id)
      if (id === chat.conversationId) chat.reset()
    } catch {
      window.alert('La suppression a échoué.')
    }
  }

  return (
    <div className="flex h-dvh bg-slate-50 dark:bg-slate-900">
      <Sidebar
        conversations={conversations}
        activeId={chat.conversationId}
        error={error}
        isOpen={sidebarOpen}
        onSelect={select}
        onNew={startNew}
        onDelete={removeConversation}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center gap-3 border-b border-slate-200 px-4 py-3 dark:border-slate-700">
          <button
            onClick={() => setSidebarOpen(true)}
            aria-label="Afficher les conversations"
            className="rounded-lg px-2 py-1 text-slate-600 hover:bg-slate-200 md:hidden dark:text-slate-300 dark:hover:bg-slate-800"
          >
            ☰
          </button>
          <h1 className="text-lg font-bold text-emerald-700 dark:text-emerald-400">SobaAI</h1>
          <div className="ml-auto flex min-w-0 items-center gap-3">
            <span className="hidden truncate text-sm text-slate-500 sm:inline">{user.email}</span>
            <button
              onClick={onLogout}
              className="shrink-0 rounded-lg px-3 py-1 text-sm text-slate-600 hover:bg-slate-200 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              Déconnexion
            </button>
          </div>
        </header>

        <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col overflow-hidden px-4">
          {chat.isLoading ? (
            <div className="flex flex-1 items-center justify-center text-slate-400">
              Chargement…
            </div>
          ) : (
            <ChatWindow messages={chat.messages} />
          )}
          <div className="py-4">
            <ChatInput isStreaming={chat.isStreaming} onSend={chat.send} onStop={chat.stop} />
          </div>
        </main>
      </div>
    </div>
  )
}
