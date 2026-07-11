import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useUser } from '../context/UserContext'
import Spinner from '../components/Spinner'
import {
  analyze,
  fetchProfessorPapers,
  getProfessorPapersCache,
  searchProfessors,
} from '../api/endpoints'
import type { Language, Provider } from '../api/types'

export default function SearchPage() {
  const { user } = useUser()
  const navigate = useNavigate()

  const [nameQuery, setNameQuery] = useState('')
  const [submittedName, setSubmittedName] = useState('')
  const [selectedAuthorId, setSelectedAuthorId] = useState<string | null>(null)
  const [interest, setInterest] = useState('')
  const [language, setLanguage] = useState<Language>('English')
  const [provider, setProvider] = useState<Provider>('anthropic')
  const [error, setError] = useState<string | null>(null)

  const searchQuery = useQuery({
    queryKey: ['professors', 'search', submittedName],
    queryFn: () => searchProfessors(submittedName),
    enabled: submittedName.trim().length > 0,
  })

  const submitMutation = useMutation({
    mutationFn: async () => {
      if (!user || !selectedAuthorId) return
      const candidate = searchQuery.data?.find((c) => c.authorId === selectedAuthorId)
      if (!candidate) return

      const authorIdNum = Number(selectedAuthorId)
      let cache = await getProfessorPapersCache(authorIdNum)
      if (cache === null) {
        cache = await fetchProfessorPapers(authorIdNum, candidate.name)
      }

      const analysis = await analyze({
        author_id: authorIdNum,
        author_name: candidate.name,
        interest,
        language,
        provider,
      })

      return { analysis, papers: cache.papers, professorName: candidate.name }
    },
    onSuccess: (result) => {
      if (!result) return
      navigate('/results', { state: result })
    },
  })

  if (!user) return <Navigate to="/login" replace />

  return (
    <div className="max-w-2xl mx-auto mt-10 space-y-6">
      <h1 className="text-2xl font-semibold">Search a professor</h1>

      <div className="flex gap-2">
        <input
          className="flex-1 border rounded px-3 py-2"
          value={nameQuery}
          onChange={(e) => setNameQuery(e.target.value)}
          placeholder="Enter a professor's name"
        />
        <button
          className="bg-sky-500 text-white rounded px-4 py-2 disabled:opacity-50 hover:bg-sky-600"
          disabled={!nameQuery.trim()}
          onClick={() => {
            setSelectedAuthorId(null)
            setSubmittedName(nameQuery.trim())
          }}
        >
          Search
        </button>
      </div>

      {searchQuery.isLoading ? (
        <div className="flex items-center gap-2">
          <Spinner />
          <h1 className="text-base">Searching...</h1>
        </div>
      ) : (
        searchQuery.isFetching && (
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Spinner size="h-3 w-3" />
            <p>Updating...</p>
          </div>
        )
      )}
      {searchQuery.isError && <p className="text-red-600">Search failed, please try again later.</p>}
      {searchQuery.data?.length === 0 && <p>No professors found.</p>}

      {searchQuery.data && searchQuery.data.length > 0 && (
        <ul className="divide-y border rounded bg-white">
          {searchQuery.data.map((candidate) => (
            <li
              key={candidate.authorId}
              className={`p-3 cursor-pointer ${
                selectedAuthorId === candidate.authorId ? 'bg-sky-100' : ''
              }`}
              onClick={() => setSelectedAuthorId(candidate.authorId)}
            >
              <div className="font-medium">{candidate.name}</div>
              <div className="text-sm text-gray-500">
                {candidate.affiliations?.join(', ') || 'No affiliation info'} · {candidate.paperCount ?? 0} papers
              </div>
            </li>
          ))}
        </ul>
      )}

      {selectedAuthorId && (
        <div className="space-y-4 border-t pt-6">
          <div>
            <label className="block mb-1 font-medium">Your research interests</label>
            <textarea
              className="w-full border rounded px-3 py-2"
              rows={4}
              value={interest}
              onChange={(e) => setInterest(e.target.value)}
            />
          </div>

          <div className="flex gap-4">
            <div>
              <label className="block mb-1 font-medium">Language</label>
              <select
                className="border rounded px-3 py-2"
                value={language}
                onChange={(e) => setLanguage(e.target.value as Language)}
              >
                <option value="English">English</option>
                <option value="Chinese">Chinese</option>
              </select>
            </div>
            <div>
              <label className="block mb-1 font-medium">LLM Provider</label>
              <select
                className="border rounded px-3 py-2"
                value={provider}
                onChange={(e) => setProvider(e.target.value as Provider)}
              >
                <option value="anthropic">Anthropic</option>
                <option value="openai">OpenAI</option>
                <option value="deepseek">DeepSeek</option>
                <option value="gemini">Gemini</option>
              </select>
            </div>
          </div>

          <button
            className="flex items-center gap-2 bg-sky-500 text-white rounded px-4 py-2 disabled:opacity-50 hover:bg-sky-600"
            disabled={!interest.trim() || submitMutation.isPending}
            onClick={() => {
              setError(null)
              submitMutation.mutate(undefined, {
                onError: () => setError('Analysis failed, please try again later.'),
              })
            }}
          >
            {submitMutation.isPending && <Spinner color="border-white/40 border-t-white" />}
            {submitMutation.isPending ? 'Analyzing...' : 'Submit analysis'}
          </button>
          {error && <p className="text-red-600">{error}</p>}
        </div>
      )}
    </div>
  )
}
