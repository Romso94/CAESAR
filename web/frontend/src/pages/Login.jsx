import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

const Login = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
    setError('')
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')

    if (!formData.email || !formData.password) {
      setError('Veuillez remplir tous les champs')
      return
    }

    onLogin()
    navigate('/dashboard')
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-dark-800/80 backdrop-blur-md border-b border-dark-700">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <Link to="/" className="text-gray-400 hover:text-white">
            ← Retour à l'accueil
          </Link>
        </div>
      </header>

      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          <div className="card p-8">
            <h1 className="text-3xl font-bold text-white mb-6 text-center">
              CAESAR
            </h1>

            <form onSubmit={handleSubmit} className="space-y-5">
              {error && <div className="text-red-400 text-sm">{error}</div>}

              <input
                type="email"
                name="email"
                placeholder="Email"
                value={formData.email}
                onChange={handleChange}
                className="input-field"
              />

              <input
                type="password"
                name="password"
                placeholder="Mot de passe"
                value={formData.password}
                onChange={handleChange}
                className="input-field"
              />

              <button className="btn-primary w-full">
                Se connecter
              </button>
            </form>

            <p className="text-center text-gray-400 mt-6">
              Pas encore de compte ?{' '}
              <Link to="/register" className="text-primary-400">
                S'inscrire
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
