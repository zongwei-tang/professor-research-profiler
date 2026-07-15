import axios from 'axios'
import { apiClient, authClient } from './client'
import type {
  Analysis,
  AnalysisResponse,
  AnalyzeRequest,
  AnalysisJobResponse,
  AuthResponse,
  PaperCacheResponse,
  ProfessorCandidate,
} from './types'

async function errorHandler(err: unknown, fallback: string): Promise<Error> {
  if (axios.isAxiosError(err) && err.response != null) {
    return Error(err.response.data.detail)
  }
  return err instanceof Error ? err : Error(fallback)
}

export async function searchProfessors(name: string): Promise<ProfessorCandidate[]> {
  try { 
    const { data } = await apiClient.get<ProfessorCandidate[]>('/professors/search', {
      params: { name },
    })
    return data
  } catch (err) {
    throw await errorHandler(err, 'Failed to search professors')
  }
}

export async function fetchProfessorPapers(
  authorId: number,
  authorName: string,
): Promise<PaperCacheResponse> {
  try {
    const { data } = await apiClient.post<PaperCacheResponse>('/professors/papers/fetch', {
      author_id: authorId,
      author_name: authorName,
    })
    return data
  } catch (err) {
    throw await errorHandler(err, 'Failed to fetch professor papers')
  }
}

export async function getProfessorPapersCache(authorId: number): Promise<PaperCacheResponse | null> {
  try {
    const { data } = await apiClient.get<PaperCacheResponse>(`/professors/${authorId}/papers`)
    return data
  } catch (err) {
    if (axios.isAxiosError(err) && err.response?.status === 404) return null
    throw await errorHandler(err, 'Failed to load cached papers')
  }
}

export async function login(username: string, password: string): Promise<AuthResponse> {
  try {
    const { data } = await authClient.post<AuthResponse>('/users/login', { username, password })
    return data
  } catch (err) {
    throw await errorHandler(err, 'Failed to log in')
  }
}

export async function signup(username: string, password: string): Promise<AuthResponse> {
  try {
    const { data } = await authClient.post<AuthResponse>('/users/signup', { username, password })
    return data
  } catch (err) {
    throw await errorHandler(err, 'Failed to sign up')
  }
}

export async function analyze(request: AnalyzeRequest): Promise<AnalysisJobResponse> {
  try {
    const { data } = await apiClient.post<AnalysisJobResponse>('/analyze', request)
    return data
  } catch (err) {
    throw await errorHandler(err, 'Failed to submit analysis request')
  }
}

export async function getAnalysisJobStatus(jobId: string): Promise<AnalysisJobResponse> {
  try {
    const { data } = await apiClient.get<AnalysisJobResponse>(`/analyze/${jobId}`)
    return data
  } catch (err) {
    throw await errorHandler(err, 'Failed to get analysis job status')
  }
}

export async function getAnalysis(jobId: string): Promise<AnalysisResponse> {
  try {
    const { data } = await apiClient.get<AnalysisResponse>(`/analyze/${jobId}/result`)
    return data
  } catch (err) {
    throw await errorHandler(err, 'Failed to load analysis')
  }
}

export async function getHistoryList(): Promise<Analysis[]> {
  try {
    const { data } = await apiClient.get<Analysis[]>('/history')
    return data
  } catch (err) {
    throw await errorHandler(err, 'Failed to load history')
  }
}

export async function deleteHistory(historyId: number) {
  try {
    const { data } = await apiClient.delete('/history/delete/one', {
      params: { analysis_id: historyId },
    })
    return data
  } catch (err) {
    throw await errorHandler(err, 'Failed to delete history item')
  }
}

export async function deleteAllHistory() {
  try {
    const { data } = await apiClient.delete('/history/delete/list')
    return data
  } catch (err) {
    throw await errorHandler(err, 'Failed to delete history')
  }
}
