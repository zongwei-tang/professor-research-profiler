import axios from 'axios'
import { apiClient } from './client'
import type {
  AnalysisResponse,
  AnalyzeRequest,
  PaperCacheResponse,
  ProfessorCandidate,
  User,
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

export async function login(username: string): Promise<User> {
  const { data } = await apiClient.post<User>('/users/login', { username })
  return data
}

export async function analyze(request: AnalyzeRequest): Promise<AnalysisResponse> {
  const { data } = await apiClient.post<AnalysisResponse>('/analyze', request)
  return data
}

export async function getHistoryList(userId: number): Promise<AnalysisResponse[]> {
  const { data } = await apiClient.get<AnalysisResponse[]>('/history', {
    params: { user_id: userId },
  })
  return data
}

export async function deleteHistory(historyId: number, userId: number){
  const {data} = await apiClient.delete('/history/delete/one', {
    params: {
      analysis_id: historyId,
      user_id: userId
    }
  })
  return data
}

export async function deleteAllHistory(userId: number) {
  const { data } = await apiClient.delete('/history/delete/list', {
    params: {
      user_id: userId
    }
  })
  return data
}
