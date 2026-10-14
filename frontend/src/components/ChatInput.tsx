import { useState, type FormEvent, type KeyboardEvent } from 'react'

interface Props {
  isStreaming: boolean
  onSend: (text: string) => void
  onStop: () => void
}

export function ChatInput({ isStreaming, onSend, onStop }: Props) {
  const [text, setText] = useState('')

  const submit = (e?: FormEvent) => {
    e?.preventDefault()
    const value = text.trim()
    if (!value || isStreaming) return
    onSend(value)
    setText('')
  }

  // Entrée = envoyer, Maj+Entrée = retour à la ligne
  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) submit(e)
  }

  return (
    <form onSubmit={submit} className="flex items-end gap-2">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={onKeyDown}
        rows={1}
        placeholder="Écrivez votre message…"
        className="max-h-40 flex-1 resize-none rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none focus:border-emerald-500 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
      />
      {isStreaming ? (
        <button
          type="button"
          onClick={onStop}
          className="rounded-xl bg-slate-500 px-4 py-3 font-medium text-white hover:bg-slate-600"
        >
          Arrêter
        </button>
      ) : (
        <button
          type="submit"
          disabled={!text.trim()}
          className="rounded-xl bg-emerald-600 px-4 py-3 font-medium text-white hover:bg-emerald-700 disabled:opacity-40"
        >
          Envoyer
        </button>
      )}
    </form>
  )
}
