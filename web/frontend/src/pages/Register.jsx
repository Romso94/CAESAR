import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

const Register = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
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

    if (!formData.name || !formData.email || !formData.password || !formData.confirmPassword) {
      setError('Veuillez remplir tous les champs')
      return
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas')
      return
    }

    if (formData.password.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères')
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
              Créer un compte
            </h1>

            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <div className="text-red-400 text-sm">
                  {error}
                </div>
              )}

              <input
                name="name"
                placeholder="Nom complet"
                value={formData.name}
                onChange={handleChange}
                className="input-field"
              />

              <input
                name="email"
                type="email"
                placeholder="Email"
                value={formData.email}
                onChange={handleChange}
                className="input-field"
              />

              <input
                name="password"
                type="password"
                placeholder="Mot de passe"
                value={formData.password}
                onChange={handleChange}
                className="input-field"
              />

              <input
                name="confirmPassword"
                type="password"
                placeholder="Confirmer mot de passe"
                value={formData.confirmPassword}
                onChange={handleChange}
                className="input-field"
              />

              <button className="btn-primary w-full">
                Créer mon compte
              </button>
            </form>

            <p className="text-center text-gray-400 mt-6">
              Déjà un compte ?{' '}
              <Link to="/login" className="text-primary-400">
                Se connecter
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Register
