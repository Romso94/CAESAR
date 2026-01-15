import { Link } from 'react-router-dom'

const Home = () => {
  const features = [
    {
      icon: '🔍',
      title: 'Scan Automatique',
      description: 'Détection automatique des vulnérabilités sur vos serveurs et réseaux',
    },
    {
      icon: '📋',
      title: 'Rapports Détaillés',
      description: 'Rapports complets avec recommandations de remédiation',
    },
    {
      icon: '💰',
      title: 'Économique',
      description: 'Solution accessible pour TPE et PME à moindre coût',
    },
    {
      icon: '⚡',
      title: 'Rapide',
      description: 'Analyses rapides et résultats instantanés',
    },
    {
      icon: '🛡️',
      title: 'Sécurité Renforcée',
      description: 'Réduisez les risques de cyberattaque efficacement',
    },
    {
      icon: '🎯',
      title: 'Simple d\'utilisation',
      description: 'Interface intuitive, configuration en quelques clics',
    },
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Background Gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary-900/20 via-dark-900 to-dark-900"></div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-32">
          <div className="text-center">
            {/* Logo */}
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-700 rounded-3xl mb-6 shadow-2xl">
              <span className="text-4xl">🛡️</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 bg-gradient-to-r from-white via-gray-100 to-gray-300 bg-clip-text text-transparent">
              CAESAR
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-300 mb-4 max-w-3xl mx-auto">
              Scan de Vulnérabilité Automatique
            </p>
            
            <p className="text-lg text-gray-400 mb-12 max-w-2xl mx-auto leading-relaxed">
              Renforcez la sécurité de votre entreprise à moindre coût. 
              Solution de pentest automatisé pour TPE et PME.
            </p>
            
            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link to="/register" className="btn-primary text-lg px-8 py-4">
                Commencer gratuitement
              </Link>
              <Link to="/login" className="btn-secondary text-lg px-8 py-4">
                Se connecter
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">
            Pourquoi choisir CAESAR ?
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Une solution complète de sécurité adaptée aux besoins des petites et moyennes entreprises
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="card p-8 hover:border-primary-500/50 transition-all duration-300 hover:transform hover:-translate-y-2"
            >
              <div className="text-5xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
              <p className="text-gray-400 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* About Section */}
      <div className="bg-dark-800/50 border-y border-dark-700 py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-6">
              À propos du projet
            </h2>
          </div>
          
          <div className="card p-8 md:p-12 space-y-6">
            <div>
              <h3 className="text-2xl font-bold text-white mb-4">🎯 Notre Mission</h3>
              <p className="text-gray-300 leading-relaxed text-lg">
                CAESAR consiste en un scan de vulnérabilité (pentest) automatique d'un poste ou d'un réseau 
                à l'aide d'un agent que l'on déploie. Cet agent rédige automatiquement un rapport détaillé 
                sur les différents tests effectués, les vulnérabilités trouvées et les remédiations possibles.
              </p>
            </div>
            
            <div>
              <h3 className="text-2xl font-bold text-white mb-4">💼 Pour qui ?</h3>
              <p className="text-gray-300 leading-relaxed text-lg">
                Ce projet a pour but d'aider les TPE et les PME à renforcer leur sécurité à moindre coût. 
                Un pentest réel peut parfois être trop cher pour ces entreprises qui n'ont pas forcément 
                beaucoup de moyens. Grâce à CAESAR, tout le monde peut renforcer sa sécurité et ainsi 
                réduire au maximum le risque de cyberattaque.
              </p>
            </div>
            
            <div>
              <h3 className="text-2xl font-bold text-white mb-4">✨ Fonctionnalités</h3>
              <ul className="space-y-3 text-gray-300 text-lg">
                <li className="flex items-start">
                  <span className="text-primary-400 mr-3">✓</span>
                  <span>Configuration simple de vos serveurs</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-400 mr-3">✓</span>
                  <span>Scans automatiques réguliers</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-400 mr-3">✓</span>
                  <span>Rapports détaillés avec recommandations</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-400 mr-3">✓</span>
                  <span>Interface intuitive et moderne</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-white mb-4">
            Prêt à commencer ?
          </h2>
          <p className="text-xl text-gray-400">
            Choisissez votre option pour accéder à CAESAR
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <Link
            to="/register"
            className="card p-8 hover:border-primary-500/50 transition-all duration-300 hover:transform hover:-translate-y-2 group"
          >
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl mb-6 group-hover:scale-110 transition-transform">
                <span className="text-3xl">🚀</span>
              </div>
              <h3 className="text-2xl font-bold text-white mb-4">Nouveau compte</h3>
              <p className="text-gray-400 mb-6">
                Créez votre compte gratuitement et commencez à sécuriser vos systèmes dès aujourd'hui
              </p>
              <span className="btn-primary inline-block">
                S'inscrire
              </span>
            </div>
          </Link>

          <Link
            to="/login"
            className="card p-8 hover:border-primary-500/50 transition-all duration-300 hover:transform hover:-translate-y-2 group"
          >
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-green-500 to-green-700 rounded-2xl mb-6 group-hover:scale-110 transition-transform">
                <span className="text-3xl">🔐</span>
              </div>
              <h3 className="text-2xl font-bold text-white mb-4">Connexion</h3>
              <p className="text-gray-400 mb-6">
                Connectez-vous à votre compte existant pour accéder à votre tableau de bord
              </p>
              <span className="btn-primary inline-block">
                Se connecter
              </span>
            </div>
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-dark-900/50 border-t border-dark-700 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
              <div className="text-xl font-bold bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
                CAESAR
              </div>
              <p className="text-sm text-gray-400 mt-1">Security Scanner</p>
            </div>
            <p className="text-sm text-gray-400 text-center md:text-right">
              © 2025 CAESAR - Scan de Vulnérabilité Automatique
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Home
