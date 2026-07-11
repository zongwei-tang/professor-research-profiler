import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Navigate } from 'react-router-dom'
import { useUser } from '../context/UserContext'
import { getHistoryList, deleteHistory, deleteAllHistory } from '../api/endpoints'
import Spinner from '../components/Spinner'


export default function HistoryPage() {
  const { user } = useUser()
  const [openId, setOpenId] = useState<number | null>(null)
  const [provider, setProvider] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const historyQuery = useQuery({
    queryKey: ['history', user?.user_id],
    queryFn: () => getHistoryList(),
    enabled: !!user,
  })

  const deleteMutation = useMutation({
    mutationFn: async (analysis_id: number) => await deleteHistory(analysis_id),
    onSuccess: () => queryClient.invalidateQueries({queryKey: ['history', user?.user_id]})
  })

  const deleteAllMutation = useMutation({
    mutationFn: async () => await deleteAllHistory(),
    onSuccess: () => historyQuery.refetch()
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
      {historyQuery.isError && <p className="text-red-600">Failed to load history.</p>}
      {historyQuery.data?.length === 0 && <p className="text-gray-500">No history yet.</p>}

      <select name='provider' onChange={(e) => {
        setProvider(e.target.value)
      }}>
        <option value='All'>All</option>
        <option value='anthropic'>Anthropic</option>
        <option value='openai'>OpenAI</option>
        <option value='deepseek'>Deepseek</option>
        <option value='gemini'>Gemini</option>
      </select>

      <button onClick={() => deleteAllMutation.mutate()} className='ml-50'>Clear all</button>

      <ul className="divide-y border rounded bg-white">
        {historyQuery.data?.map((item) => (
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
            <button onClick={() => deleteMutation.mutate(item.analysis_id)}>Delete</button>
            {openId === item.analysis_id && (
              <div className="mt-2 space-y-2">
                <p className="text-sm text-gray-500">Interest: {item.interest}</p>
                <p className="whitespace-pre-wrap leading-relaxed">{item.analysis_text}</p>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}
