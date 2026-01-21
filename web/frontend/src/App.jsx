import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import ServerConfig from './pages/ServerConfig'
import ScanResults from './pages/ScanResults'
import UsersList from './pages/UsersList'
import Layout from './components/Layout'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Vérifier si l'utilisateur est connecté via le token JWT
    const checkAuth = async () => {
      const token = localStorage.getItem('caesar_token')
      
      if (token) {
        try {
          // Vérifier que le token est valide en appelant l'API
          const { authAPI } = await import('./services/api')
          await authAPI.getMe()
          setIsAuthenticated(true)
        } catch (error) {
          // Token invalide ou expiré
          localStorage.removeItem('caesar_token')
          localStorage.removeItem('caesar_user')
          setIsAuthenticated(false)
        }
      } else {
        setIsAuthenticated(false)
      }
      
      setLoading(false)
    }

    checkAuth()
  }, [])

  const handleLogin = () => {
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
    localStorage.removeItem('caesar_token')
    localStorage.removeItem('caesar_user')
  }

  // Composant pour routes protégées
  const ProtectedRoute = () => {
    if (!isAuthenticated) {
      return <Navigate to="/login" replace />
    }
    return (
      <Layout onLogout={handleLogout}>
        <Outlet />
      </Layout>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route 
          path="/login" 
          element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login onLogin={handleLogin} />} 
        />
        <Route 
          path="/register" 
          element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Register onLogin={handleLogin} />} 
        />
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/server-config" element={<ServerConfig />} />
          <Route path="/scan-results" element={<ScanResults />} />
          <Route path="/users" element={<UsersList />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
