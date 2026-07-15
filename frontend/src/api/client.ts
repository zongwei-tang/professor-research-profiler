import axios from 'axios'

export const USER_STORAGE_KEY = 'profiler.user'
export const TOKEN_STORAGE_KEY = 'profiler.token'

export const authClient = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL ?? '/api',
})

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL ?? '/api',
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(USER_STORAGE_KEY)
      localStorage.removeItem(TOKEN_STORAGE_KEY)
      alert('Not authorized, please log in again.')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)
