import axios from 'axios'
import { apiClient, authClient } from './client'
import type {
  Analysis,
  AnalysisResponse,
  AnalyzeRequest,
  AuthResponse,
  PaperCacheResponse,
  ProfessorCandidate,
} from './types'

export async function searchProfessors(name: string): Promise<ProfessorCandidate[]> {
  const { data } = await apiClient.get<ProfessorCandidate[]>('/professors/search', {
    params: { name },
  })
  return data
}

export async function fetchProfessorPapers(
  authorId: number,
  authorName: string,
): Promise<PaperCacheResponse> {
  const { data } = await apiClient.post<PaperCacheResponse>('/professors/papers/fetch', {
    author_id: authorId,
    author_name: authorName,
  })
  return data
}

export async function getProfessorPapersCache(authorId: number): Promise<PaperCacheResponse | null> {
  try {
    const { data } = await apiClient.get<PaperCacheResponse>(`/professors/${authorId}/papers`)
    return data
  } catch (err) {
    if (axios.isAxiosError(err) && err.response?.status === 404) return null
    throw err
  }
}

export async function login(username: string, password: string): Promise<AuthResponse> {
  const { data } = await authClient.post<AuthResponse>('/users/login', { username, password })
  return data
}

export async function signup(username: string, password: string): Promise<AuthResponse> {
  const { data } = await authClient.post<AuthResponse>('/users/signup', { username, password })
  return data
}

export async function analyze(request: AnalyzeRequest): Promise<AnalysisResponse> {
  const { data } = await apiClient.post<AnalysisResponse>('/analyze', request)
  return data
}

export async function getHistoryList(): Promise<Analysis[]> {
  const { data } = await apiClient.get<Analysis[]>('/history')
  return data
}

export async function deleteHistory(historyId: number) {
  const { data } = await apiClient.delete('/history/delete/one', {
    params: { analysis_id: historyId },
  })
  return data
}

export async function deleteAllHistory() {
  const { data } = await apiClient.delete('/history/delete/list')
  return data
}
