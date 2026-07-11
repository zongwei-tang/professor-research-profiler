import { createContext, useContext, useState, type ReactNode } from 'react'
import { login as loginRequest, signup as signupRequest } from '../api/endpoints'
import { USER_STORAGE_KEY, TOKEN_STORAGE_KEY } from '../api/client'
import type { User } from '../api/types'

interface UserContextValue {
  user: User | null
  login: (username: string, password: string) => Promise<void>
  signup: (username: string, password: string) => Promise<void>
  logout: () => void
}

const UserContext = createContext<UserContextValue | null>(null)

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem(USER_STORAGE_KEY)
    return stored ? (JSON.parse(stored) as User) : null
  })

  function persist(loggedInUser: User, accessToken: string) {
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(loggedInUser))
    localStorage.setItem(TOKEN_STORAGE_KEY, accessToken)
    setUser(loggedInUser)
  }

  async function login(username: string, password: string) {
    const result = await loginRequest(username, password)
    persist(result.user, result.access_token)
  }

  async function signup(username: string, password: string) {
    const result = await signupRequest(username, password)
    persist(result.user, result.access_token)
  }

  function logout() {
    localStorage.removeItem(USER_STORAGE_KEY)
    localStorage.removeItem(TOKEN_STORAGE_KEY)
    setUser(null)
  }

  return <UserContext.Provider value={{ user, login, signup, logout }}>{children}</UserContext.Provider>
}

export function useUser() {
  const context = useContext(UserContext)
  if (!context) throw new Error('useUser must be used within a UserProvider')
  return context
}
