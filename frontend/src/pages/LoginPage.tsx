import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { useUser } from '../context/UserContext'
import Spinner from '../components/Spinner'

export default function LoginPage() {
  const { login, signup } = useUser()
  const navigate = useNavigate()

  const [mode, setMode] = useState<'login' | 'signup'>('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: () => (mode === 'login' ? login(username, password) : signup(username, password)),
    onSuccess: () => navigate('/'),
    onError: () => {
      setError(mode === 'login' ? 'Incorrect username or password.' : 'Username already taken.')
    },
  })

  return (
    <div className="max-w-md mx-auto mt-16 space-y-4">
      <h1 className="text-2xl font-semibold">{mode === 'login' ? 'Log in' : 'Create an account'}</h1>
      <input
        className="w-full border rounded px-3 py-2"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
      />
      <input
        className="w-full border rounded px-3 py-2"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button
        className="w-full flex items-center justify-center gap-2 bg-sky-500 text-white rounded py-2 disabled:opacity-50 hover:bg-sky-600"
        disabled={!username.trim() || !password.trim() || mutation.isPending}
        onClick={() => {
          setError(null)
          mutation.mutate()
        }}
      >
        {mutation.isPending && <Spinner color="border-white/40 border-t-white" />}
        {mode === 'login' ? 'Log in' : 'Sign up'}
      </button>
      {error && <p className="text-red-600">{error}</p>}
      <button
        className="text-sm text-sky-600"
        onClick={() => {
          setMode(mode === 'login' ? 'signup' : 'login')
          setError(null)
        }}
      >
        {mode === 'login' ? "Don't have an account? Sign up" : 'Already have an account? Log in'}
      </button>
    </div>
  )
}
