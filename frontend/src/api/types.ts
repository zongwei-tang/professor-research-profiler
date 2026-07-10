export interface ProfessorCandidate {
  authorId: string
  name: string
  affiliations: string[] | null
  paperCount: number | null
  citationCount: number | null
  hIndex: number | null
}

export interface PaperAuthor {
  authorId: string | null
  name: string
}

export interface Paper {
  title: string
  year: number | null
  abstract: string | null
  citationCount: number | null
  authors: PaperAuthor[]
  fieldsOfStudy: string[] | null
  openAccessPdf: { url: string } | null
  venue: string | null
}

export interface PaperCacheResponse {
  papers: Paper[]
  time: string | null
}

export interface User {
  user_id: number
  username: string
}

export type Provider = 'anthropic' | 'openai' | 'deepseek' | 'gemini'
export type Language = 'English' | 'Chinese'

export interface AnalyzeRequest {
  user_id: number
  author_id: number
  author_name: string
  interest: string
  language: Language
  provider: Provider
}

export interface AnalysisResponse {
  analysis_id: number
  user_id: number
  author_id: number
  author_name: string
  analysis_text: string
  time: string | null
  interest: string
  language: string
  provider: string
}