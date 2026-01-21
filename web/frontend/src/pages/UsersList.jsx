import { useState, useEffect } from 'react'
import { authAPI } from '../services/api'

const UsersList = () => {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      const response = await authAPI.getUsers()
      setUsers(response.data.users)
      setError('')
    } catch (err) {
      setError(err.message || 'Erreur lors du chargement des utilisateurs')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">Liste des Utilisateurs</h1>
        <p className="text-gray-400">
          {users.length} utilisateur{users.length > 1 ? 's' : ''} inscrit{users.length > 1 ? 's' : ''}
        </p>
      </div>

      {error && (
        <div className="card p-4 bg-red-500/10 border border-red-500/50">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {users.length === 0 ? (
        <div className="card p-12 text-center">
          <span className="text-6xl mb-4 block">👤</span>
          <p className="text-gray-400">Aucun utilisateur inscrit</p>
        </div>
      ) : (
        <div className="card p-6">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-dark-700">
                  <th className="text-left py-3 px-4 text-gray-300 font-semibold">Nom</th>
                  <th className="text-left py-3 px-4 text-gray-300 font-semibold">Email</th>
                  <th className="text-left py-3 px-4 text-gray-300 font-semibold">Date d'inscription</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id || user._id} className="border-b border-dark-700/50 hover:bg-dark-700/30 transition-colors">
                    <td className="py-4 px-4 text-white">{user.name}</td>
                    <td className="py-4 px-4 text-gray-300">{user.email}</td>
                    <td className="py-4 px-4 text-gray-400">
                      {new Date(user.createdAt).toLocaleDateString('fr-FR', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <button
        onClick={fetchUsers}
        className="btn-secondary"
      >
        🔄 Actualiser
      </button>
    </div>
  )
}

export default UsersList
