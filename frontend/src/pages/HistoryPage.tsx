import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Navigate } from 'react-router-dom'
import { useUser } from '../context/UserContext'
import { getHistoryList, deleteHistory, deleteAllHistory } from '../api/endpoints'
import Spinner from '../components/Spinner'
import ErrorMessage from '../components/ErrorMessage'


export default function HistoryPage() {
  const { user } = useUser()
  const [openId, setOpenId] = useState<number | null>(null)
  const [provider, setProvider] = useState<string | null>(null)
  const queryClient = useQueryClient()
  const [deleteError, setDeleteError] = useState<string | null>(null)

  const historyQuery = useQuery({
    queryKey: ['history', user?.user_id],
    queryFn: () => getHistoryList(),
    enabled: !!user,
    staleTime: 5 * 60 * 1000,
  })

  const deleteMutation = useMutation({
    mutationFn: async (analysis_id: number) => await deleteHistory(analysis_id),
    onSuccess: () => queryClient.invalidateQueries({queryKey: ['history', user?.user_id]}),
    onError: async (err) => {
      const message = err instanceof Error ? err.message : 'Failed to delete history item'
      setDeleteError(message)
    }
  })

  const deleteAllMutation = useMutation({
    mutationFn: async () => await deleteAllHistory(),
    onSuccess: () => historyQuery.refetch(),
    onError: async (err) => {
      const message = err instanceof Error ? err.message : 'Failed to delete all history items'
      setDeleteError(message)
    }
  })

  if (!user) return <Navigate to="/login" replace />

  return (
    <div className="max-w-3xl mx-auto mt-10 space-y-4">
      <h1 className="text-2xl font-semibold">History</h1>

      {historyQuery.isLoading && (
        <div className="flex items-center gap-2">
          <Spinner />
          <p>Loading...</p>
        </div>
      )}
      {!historyQuery.isLoading && historyQuery.isFetching && (
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Spinner size="h-3 w-3" />
          <p>Updating...</p>
        </div>
      )}
      {historyQuery.isError && (
        <ErrorMessage message={historyQuery.error instanceof Error ? historyQuery.error.message : 'Failed to load history.'} />
      )}
      {deleteError && <ErrorMessage message={deleteError} />}
      {historyQuery.data?.length === 0 && <p className="text-gray-500">No history yet.</p>}

      <div className="flex items-center justify-between">
        <select
          name='provider'
          className="border rounded px-3 py-2"
          onChange={(e) => {
            setProvider(e.target.value)
          }}
        >
          <option value='All'>All</option>
          <option value='anthropic'>Anthropic</option>
          <option value='openai'>OpenAI</option>
          <option value='deepseek'>Deepseek</option>
          <option value='gemini'>Gemini</option>
        </select>

        <button
          onClick={() => {
            setDeleteError(null)
            deleteAllMutation.mutate()
          }}
          disabled={deleteAllMutation.isPending}
          className="flex items-center gap-2 disabled:opacity-50"
        >
          {deleteAllMutation.isPending && <Spinner size="h-3 w-3" />}
          {deleteAllMutation.isPending ? 'Clearing...' : 'Clear all'}
        </button>
      </div>

      <ul className="divide-y border rounded bg-white">
        {historyQuery.data?.map((item) => {
          const isDeletingThis = deleteMutation.isPending && deleteMutation.variables === item.analysis_id
          return (
          (item.provider === provider || provider === null || provider === 'All') && <li key={item.analysis_id} className="p-3">
            <button
              className="w-full text-left"
              onClick={() => setOpenId(openId === item.analysis_id ? null : item.analysis_id)}
            >
              <div className="font-medium">{item.author_name}</div>
              <div className="text-sm text-gray-500">
                {item.provider} · {item.language} · {item.time}
              </div>
            </button>
            <button
              className="flex items-center gap-2 disabled:opacity-50"
              onClick={() => {
                setDeleteError(null)
                deleteMutation.mutate(item.analysis_id)
              }}
              disabled={isDeletingThis}
            >
              {isDeletingThis && <Spinner size="h-3 w-3" />}
              {isDeletingThis ? 'Deleting...' : 'Delete'}
            </button>
            {openId === item.analysis_id && (
              <div className="mt-2 space-y-2">
                <p className="text-sm text-gray-500">Interest: {item.interest}</p>
                <p className="whitespace-pre-wrap leading-relaxed">{item.analysis_text}</p>
              </div>
            )}
          </li>
          )
        })}
      </ul>
    </div>
  )
}
