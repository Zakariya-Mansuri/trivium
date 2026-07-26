import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import { Spinner } from './components/ui'
import { useAuth } from './context/AuthContext'
import AgentChat from './pages/AgentChat'
import { Login, Signup } from './pages/Auth'
import Dashboard from './pages/Dashboard'
import ImportSession from './pages/ImportSession'
import Landing from './pages/Landing'
import Learn from './pages/Learn'
import Metrics from './pages/Metrics'
import Profile from './pages/Profile'
import Projects from './pages/Projects'
import Review from './pages/Review'
import SessionDetail from './pages/SessionDetail'
import Sessions from './pages/Sessions'
import Settings from './pages/Settings'

function Protected({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <Spinner label="Checking your session…" />
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route
        path="/app"
        element={
          <Protected>
            <Layout />
          </Protected>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="projects" element={<Projects />} />
        <Route path="sessions" element={<Sessions />} />
        <Route path="sessions/import" element={<ImportSession />} />
        <Route path="sessions/:id" element={<SessionDetail />} />
        <Route path="agent" element={<AgentChat />} />
        <Route path="learn" element={<Learn />} />
        <Route path="review" element={<Review />} />
        <Route path="profile" element={<Profile />} />
        <Route path="metrics" element={<Metrics />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
