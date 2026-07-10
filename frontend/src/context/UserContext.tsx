import { createContext, useContext, useState, type ReactNode } from 'react'
import { login as loginRequest } from '../api/endpoints'
import type { User } from '../api/types'

interface UserContextValue {
  user: User | null
  login: (username: string) => Promise<void>
  logout: () => void
}

const UserContext = createContext<UserContextValue | null>(null)

const STORAGE_KEY = 'profiler.user'

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? (JSON.parse(stored) as User) : null
  })

  async function login(username: string) {
    const loggedInUser = await loginRequest(username)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(loggedInUser))
    setUser(loggedInUser)
  }

  function logout() {
    localStorage.removeItem(STORAGE_KEY)
    setUser(null)
  }

  return <UserContext.Provider value={{ user, login, logout }}>{children}</UserContext.Provider>
}

export function useUser() {
  const context = useContext(UserContext)
  if (!context) throw new Error('useUser must be used within a UserProvider')
  return context
}
