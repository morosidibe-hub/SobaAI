import type { ChatMessage } from '../types/chat'

interface Props {
  message: ChatMessage
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] whitespace-pre-wrap rounded-2xl px-4 py-2 leading-relaxed ${
          isUser
            ? 'bg-emerald-600 text-white'
            : 'bg-white text-slate-800 shadow-sm ring-1 ring-slate-200 dark:bg-slate-800 dark:text-slate-100 dark:ring-slate-700'
        }`}
      >
        {message.content || <span className="animate-pulse text-slate-400">…</span>}
      </div>
    </div>
  )
}
