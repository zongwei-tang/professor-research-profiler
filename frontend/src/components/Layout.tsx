import { Link, Outlet } from 'react-router-dom'
import { useUser } from '../context/UserContext'

export default function Layout() {
  const { user, logout } = useUser()

  return (
    <div className="min-h-screen bg-white">
      <nav className="border-b border-sky-100 bg-white px-6 py-3 flex items-center justify-between">
        <div className="flex gap-4">
          <Link to="/" className="font-semibold text-sky-700">
            Professor Research Profiler
          </Link>
          {user && (
            <Link to="/history" className="text-gray-600">
              History
            </Link>
          )}
        </div>
        {user && (
          <div className="flex items-center gap-3 text-sm">
            <span>{user.username}</span>
            <button className="text-sky-600" onClick={logout}>
              Log out
            </button>
          </div>
        )}
      </nav>
      <main className="px-6 pb-16">
        <Outlet />
      </main>
    </div>
  )
}
