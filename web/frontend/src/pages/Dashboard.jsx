import { Link } from 'react-router-dom'

const Dashboard = () => {
  const stats = [
    {
      title: 'Scans effectués',
      value: '0',
      icon: '📊',
      color: 'from-blue-500 to-blue-600',
      link: '/scan-results',
    },
    {
      title: 'Vulnérabilités détectées',
      value: '0',
      icon: '⚠️',
      color: 'from-red-500 to-red-600',
      link: '/scan-results',
    },
    {
      title: 'Serveurs configurés',
      value: '0',
      icon: '🖥️',
      color: 'from-green-500 to-green-600',
      link: '/server-config',
    },
    {
      title: 'Taux de sécurité',
      value: '0%',
      icon: '🛡️',
      color: 'from-purple-500 to-purple-600',
      link: '/scan-results',
    },
  ]

  const recentScans = [
    // Pour l'instant vide, sera rempli plus tard avec les vraies données
  ]

  return (
    <div className="space-y-8 animate-fade-in">
      {/* En-tête */}
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-gray-400">Bienvenue sur votre tableau de bord CAESAR</p>
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <Link
            key={index}
            to={stat.link}
            className="card p-6 hover:border-primary-500/50 transition-all duration-200 group"
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${stat.color} flex items-center justify-center text-2xl shadow-lg`}>
                {stat.icon}
              </div>
            </div>
            <h3 className="text-gray-400 text-sm font-medium mb-1">{stat.title}</h3>
            <p className="text-3xl font-bold text-white">{stat.value}</p>
          </Link>
        ))}
      </div>

      {/* Actions rapides */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h2 className="text-xl font-bold text-white mb-4">Actions rapides</h2>
          <div className="space-y-3">
            <Link
              to="/server-config"
              className="flex items-center justify-between p-4 bg-dark-700/50 rounded-lg hover:bg-dark-700 transition-colors group"
            >
              <div className="flex items-center space-x-3">
                <span className="text-2xl">⚙️</span>
                <div>
                  <p className="text-white font-medium">Configurer un serveur</p>
                  <p className="text-sm text-gray-400">Ajoutez un nouveau serveur à scanner</p>
                </div>
              </div>
              <span className="text-gray-400 group-hover:text-primary-400">→</span>
            </Link>
            <Link
              to="/scan-results"
              className="flex items-center justify-between p-4 bg-dark-700/50 rounded-lg hover:bg-dark-700 transition-colors group"
            >
              <div className="flex items-center space-x-3">
                <span className="text-2xl">📋</span>
                <div>
                  <p className="text-white font-medium">Voir les résultats</p>
                  <p className="text-sm text-gray-400">Consultez vos rapports de scan</p>
                </div>
              </div>
              <span className="text-gray-400 group-hover:text-primary-400">→</span>
            </Link>
          </div>
        </div>

        <div className="card p-6">
          <h2 className="text-xl font-bold text-white mb-4">Derniers scans</h2>
          {recentScans.length > 0 ? (
            <div className="space-y-3">
              {recentScans.map((scan, index) => (
                <div
                  key={index}
                  className="p-4 bg-dark-700/50 rounded-lg border border-dark-600"
                >
                  {/* Contenu des scans */}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <span className="text-4xl mb-4 block">🔍</span>
              <p className="text-gray-400">Aucun scan effectué pour le moment</p>
              <Link
                to="/server-config"
                className="inline-block mt-4 text-primary-400 hover:text-primary-300"
              >
                Configurer votre premier serveur →
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Guide de démarrage */}
      <div className="card p-6 bg-gradient-to-r from-primary-900/20 to-primary-800/20 border-primary-700/50">
        <h2 className="text-xl font-bold text-white mb-3">🚀 Guide de démarrage</h2>
        <ol className="space-y-2 text-gray-300">
          <li className="flex items-start">
            <span className="font-bold text-primary-400 mr-2">1.</span>
            <span>Configurez votre serveur dans la section "Configuration Serveur"</span>
          </li>
          <li className="flex items-start">
            <span className="font-bold text-primary-400 mr-2">2.</span>
            <span>Lancez un scan de vulnérabilité</span>
          </li>
          <li className="flex items-start">
            <span className="font-bold text-primary-400 mr-2">3.</span>
            <span>Consultez les résultats et les recommandations de remédiation</span>
          </li>
        </ol>
      </div>
    </div>
  )
}

export default Dashboard
