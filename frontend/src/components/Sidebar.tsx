import type { Conversation } from '../types/chat'

interface Props {
  conversations: Conversation[]
  activeId: string | null
  error: string | null
  isOpen: boolean
  onSelect: (id: string) => void
  onNew: () => void
  onDelete: (id: string) => void
  onClose: () => void
}

export function Sidebar({
  conversations,
  activeId,
  error,
  isOpen,
  onSelect,
  onNew,
  onDelete,
  onClose,
}: Props) {
  return (
    <>
      {/* Fond sombre derrière le menu sur mobile */}
      {isOpen && <div className="fixed inset-0 z-10 bg-black/40 md:hidden" onClick={onClose} />}

      <aside
        className={`fixed inset-y-0 left-0 z-20 flex w-72 flex-col border-r border-slate-200 bg-white transition-transform md:static md:translate-x-0 dark:border-slate-700 dark:bg-slate-950 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="p-3">
          <button
            onClick={onNew}
            className="w-full rounded-lg border border-emerald-600 px-3 py-2 text-sm font-medium text-emerald-700 hover:bg-emerald-50 dark:text-emerald-400 dark:hover:bg-emerald-950"
          >
            + Nouvelle conversation
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto px-2 pb-3">
          {error && <p className="px-2 text-sm text-amber-600">{error}</p>}
          {!error && conversations.length === 0 && (
            <p className="px-2 text-sm text-slate-400">Aucune conversation pour l'instant.</p>
          )}
          <ul className="space-y-1">
            {conversations.map((c) => (
              <li key={c.id} className="group relative">
                <button
                  onClick={() => onSelect(c.id)}
                  title={c.title}
                  className={`w-full truncate rounded-lg py-2 pr-8 pl-3 text-left text-sm ${
                    c.id === activeId
                      ? 'bg-emerald-100 font-medium text-emerald-900 dark:bg-emerald-900/40 dark:text-emerald-100'
                      : 'text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
                  }`}
                >
                  {c.title}
                </button>
                <button
                  onClick={() => onDelete(c.id)}
                  aria-label={`Supprimer « ${c.title} »`}
                  className="absolute top-1/2 right-1 -translate-y-1/2 rounded px-2 py-1 text-slate-400 opacity-100 hover:text-red-600 md:opacity-0 md:group-hover:opacity-100 md:focus:opacity-100"
                >
                  ✕
                </button>
              </li>
            ))}
          </ul>
        </nav>
      </aside>
    </>
  )
}
