import { AuthPage } from './components/AuthPage'
import { ChatApp } from './components/ChatApp'
import { useAuth } from './hooks/useAuth'

export default function App() {
  const { user, isLoading, login, register, logout } = useAuth()

  if (isLoading) {
    return (
      <div className="flex h-dvh items-center justify-center bg-slate-50 text-slate-400 dark:bg-slate-900">
        Chargement…
      </div>
    )
  }

  if (!user) return <AuthPage onLogin={login} onRegister={register} />

  // key : l'état du chat repart de zéro si un autre utilisateur se connecte.
  return <ChatApp key={user.id} user={user} onLogout={logout} />
}
