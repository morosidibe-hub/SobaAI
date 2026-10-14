import { useEffect, useRef } from 'react'

import type { ChatMessage } from '../types/chat'
import { MessageBubble } from './MessageBubble'

interface Props {
  messages: ChatMessage[]
}

export function ChatWindow({ messages }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center text-center text-slate-500">
        <p className="text-2xl font-semibold text-slate-700 dark:text-slate-200">
          Bonjour, je suis SobaAI 👋
        </p>
        <p className="mt-2">Posez-moi une question pour commencer.</p>
      </div>
    )
  }

  return (
    <div className="flex flex-1 flex-col gap-3 overflow-y-auto py-4">
      {messages.map((m, i) => (
        <MessageBubble key={i} message={m} />
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
