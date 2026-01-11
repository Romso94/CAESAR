import { useState } from 'react'

const ServerConfig = () => {
  const [formData, setFormData] = useState({
    name: '',
    host: '',
    port: '22',
    type: 'ssh',
    username: '',
    password: '',
    description: '',
  })
  const [servers, setServers] = useState([])
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
    setError('')
    setSuccess('')
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    // Validation
    if (!formData.name || !formData.host || !formData.username) {
      setError('Veuillez remplir tous les champs obligatoires')
      return
    }

    // Ajouter le serveur à la liste (simulation)
    const newServer = {
      id: Date.now(),
      ...formData,
      createdAt: new Date().toLocaleDateString('fr-FR'),
    }
    setServers([...servers, newServer])
    setSuccess('Serveur configuré avec succès !')
    
    // Réinitialiser le formulaire
    setFormData({
      name: '',
      host: '',
      port: '22',
      type: 'ssh',
      username: '',
      password: '',
      description: '',
    })
  }

  const handleDelete = (id) => {
    setServers(servers.filter(server => server.id !== id))
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* En-tête */}
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">Configuration Serveur</h1>
        <p className="text-gray-400">Configurez vos serveurs pour les scans de vulnérabilité</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Formulaire */}
        <div className="lg:col-span-2">
          <div className="card p-6">
            <h2 className="text-2xl font-bold text-white mb-6">Ajouter un serveur</h2>

            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <div className="bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg text-sm">
                  {error}
                </div>
              )}

              {success && (
                <div className="bg-green-500/10 border border-green-500/50 text-green-400 px-4 py-3 rounded-lg text-sm">
                  {success}
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="md:col-span-2">
                  <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-2">
                    Nom du serveur <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="Serveur Production"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="host" className="block text-sm font-medium text-gray-300 mb-2">
                    Adresse IP / Hostname <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    id="host"
                    name="host"
                    value={formData.host}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="192.168.1.100"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="port" className="block text-sm font-medium text-gray-300 mb-2">
                    Port
                  </label>
                  <input
                    type="number"
                    id="port"
                    name="port"
                    value={formData.port}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="22"
                  />
                </div>

                <div>
                  <label htmlFor="type" className="block text-sm font-medium text-gray-300 mb-2">
                    Type de connexion
                  </label>
                  <select
                    id="type"
                    name="type"
                    value={formData.type}
                    onChange={handleChange}
                    className="input-field"
                  >
                    <option value="ssh">SSH</option>
                    <option value="https">HTTPS</option>
                    <option value="http">HTTP</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="username" className="block text-sm font-medium text-gray-300 mb-2">
                    Nom d'utilisateur <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    id="username"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="admin"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                    Mot de passe
                  </label>
                  <input
                    type="password"
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="••••••••"
                  />
                </div>

                <div className="md:col-span-2">
                  <label htmlFor="description" className="block text-sm font-medium text-gray-300 mb-2">
                    Description
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    className="input-field"
                    rows="3"
                    placeholder="Description optionnelle du serveur..."
                  />
                </div>
              </div>

              <button type="submit" className="btn-primary w-full md:w-auto">
                Ajouter le serveur
              </button>
            </form>
          </div>
        </div>

        {/* Liste des serveurs */}
        <div className="lg:col-span-1">
          <div className="card p-6">
            <h2 className="text-xl font-bold text-white mb-4">Serveurs configurés</h2>
            {servers.length > 0 ? (
              <div className="space-y-3">
                {servers.map((server) => (
                  <div
                    key={server.id}
                    className="p-4 bg-dark-700/50 rounded-lg border border-dark-600"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="font-semibold text-white">{server.name}</h3>
                        <p className="text-sm text-gray-400">{server.host}:{server.port}</p>
                      </div>
                      <button
                        onClick={() => handleDelete(server.id)}
                        className="text-red-400 hover:text-red-300 text-sm"
                      >
                        ✕
                      </button>
                    </div>
                    <div className="flex items-center space-x-2 mt-2">
                      <span className="text-xs bg-primary-500/20 text-primary-300 px-2 py-1 rounded">
                        {server.type.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500">{server.createdAt}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <span className="text-4xl mb-4 block">🖥️</span>
                <p className="text-gray-400 text-sm">Aucun serveur configuré</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ServerConfig
