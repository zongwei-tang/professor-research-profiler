import { useMemo } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { AnalysisResponse, Paper } from '../api/types'

const ACCENT = '#2a78d6'
const GRID = '#e1e0d9'
const MUTED_INK = '#898781'

interface ResultsState {
  analysis: AnalysisResponse
  papers: Paper[]
  professorName: string
}

export default function ResultsPage() {
  const location = useLocation()
  let state: ResultsState | null = null
  if (location.state) {
    sessionStorage.setItem('state', JSON.stringify(location.state))
    state = location.state
  } else{
    state = JSON.parse(sessionStorage.getItem('state')!)
  }

  const byYear = useMemo(() => {
    if (!state) return []
    const counts = new Map<number, number>()
    for (const paper of state.papers) {
      if (paper.year == null) continue
      counts.set(paper.year, (counts.get(paper.year) ?? 0) + 1)
    }
    return [...counts.entries()]
      .sort(([a], [b]) => a - b)
      .map(([year, count]) => ({ year: String(year), count }))
  }, [state])

  const topCoauthors = useMemo(() => {
    if (!state) return []
    const counts = new Map<string, number>()
    for (const paper of state.papers) {
      for (const author of paper.authors) {
        if (author.name === state.professorName) continue
        counts.set(author.name, (counts.get(author.name) ?? 0) + 1)
      }
    }
    return [...counts.entries()]
      .sort(([, a], [, b]) => b - a)
      .slice(0, 8)
  }, [state])

  if (!state) {
    return (
      <div className="max-w-2xl mx-auto mt-16 text-center space-y-4">
        <p>No analysis result to show.</p>
        <Link to="/" className="text-sky-600 underline">
          Back to search
        </Link>
      </div>
    )
  }

  const { analysis, professorName } = state


  return (
    <div className="max-w-3xl mx-auto mt-10 space-y-8">
      <div>
        <h1 className="text-2xl font-semibold">{professorName}</h1>
        <p className="text-sm text-gray-500">
          {analysis.provider} · {analysis.language} · {analysis.time}
        </p>
      </div>

      <section>
        <h2 className="text-lg font-medium mb-2">Papers by year</h2>
        {byYear.length === 0 ? (
          <p className="text-gray-500">No year information available.</p>
        ) : (
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={byYear} barSize={24}>
              <CartesianGrid vertical={false} stroke={GRID} strokeWidth={1} />
              <XAxis dataKey="year" tick={{ fill: MUTED_INK, fontSize: 12 }} axisLine={{ stroke: GRID }} tickLine={false} />
              <YAxis allowDecimals={false} tick={{ fill: MUTED_INK, fontSize: 12 }} axisLine={false} tickLine={false} />
              <Tooltip cursor={{ fill: 'rgba(42, 120, 214, 0.08)' }} />
              <Bar dataKey="count" name="Papers" fill={ACCENT} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </section>

      <section>
        <h2 className="text-lg font-medium mb-2">Frequent collaborators</h2>
        {topCoauthors.length === 0 ? (
          <p className="text-gray-500">No collaborator information available.</p>
        ) : (
          <ul className="flex flex-wrap gap-2">
            {topCoauthors.map(([name, count]) => (
              <li key={name} className="border rounded-full px-3 py-1 text-sm">
                {name} · {count}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2 className="text-lg font-medium mb-2">LLM analysis</h2>
        <p className="whitespace-pre-wrap leading-relaxed">{analysis.analysis_text}</p>
      </section>

      <Link to="/" className="inline-block text-sky-600 underline">
        Search another professor
      </Link>
    </div>
  )
}
