import { useState, type FormEvent } from 'react'

const MIN_PASSWORD_LENGTH = 8

interface Props {
  onLogin: (email: string, password: string) => Promise<void>
  onRegister: (email: string, password: string) => Promise<void>
}

export function AuthPage({ onLogin, onRegister }: Props) {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const isRegister = mode === 'register'

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await (isRegister ? onRegister : onLogin)(email, password)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue')
      setIsSubmitting(false)
    }
  }

  const switchMode = () => {
    setMode(isRegister ? 'login' : 'register')
    setError(null)
  }

  const inputClass =
    'w-full rounded-lg border border-slate-300 bg-white px-3 py-2 outline-none focus:border-emerald-500 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100'

  return (
    <div className="flex min-h-dvh items-center justify-center bg-slate-50 px-4 dark:bg-slate-900">
      <form
        onSubmit={submit}
        className="w-full max-w-sm space-y-4 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200 dark:bg-slate-950 dark:ring-slate-800"
      >
        <div className="text-center">
          <h1 className="text-2xl font-bold text-emerald-700 dark:text-emerald-400">SobaAI</h1>
          <p className="mt-1 text-sm text-slate-500">
            {isRegister ? 'Créez votre compte' : 'Connectez-vous pour continuer'}
          </p>
        </div>

        <label className="block space-y-1">
          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Email</span>
          <input
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={inputClass}
          />
        </label>

        <label className="block space-y-1">
          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
            Mot de passe
          </span>
          <input
            type="password"
            required
            minLength={isRegister ? MIN_PASSWORD_LENGTH : undefined}
            autoComplete={isRegister ? 'new-password' : 'current-password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={inputClass}
          />
          {isRegister && (
            <span className="text-xs text-slate-400">
              Au moins {MIN_PASSWORD_LENGTH} caractères
            </span>
          )}
        </label>

        {error && (
          <p
            role="alert"
            className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950 dark:text-red-300"
          >
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full rounded-lg bg-emerald-600 py-2 font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
        >
          {isSubmitting ? '…' : isRegister ? 'Créer mon compte' : 'Se connecter'}
        </button>

        <p className="text-center text-sm text-slate-500">
          {isRegister ? 'Déjà un compte ?' : 'Pas encore de compte ?'}{' '}
          <button
            type="button"
            onClick={switchMode}
            className="font-medium text-emerald-700 hover:underline dark:text-emerald-400"
          >
            {isRegister ? 'Se connecter' : "S'inscrire"}
          </button>
        </p>
      </form>
    </div>
  )
}
