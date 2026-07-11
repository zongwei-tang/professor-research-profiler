import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import SearchPage from './pages/SearchPage'
import ResultsPage from './pages/ResultsPage'
import HistoryPage from './pages/HistoryPage'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<SearchPage />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="/history" element={<HistoryPage />} />
      </Route>
    </Routes>
  )
}
