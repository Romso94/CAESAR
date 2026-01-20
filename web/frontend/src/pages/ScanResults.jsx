import { useState } from 'react'
import { Link } from 'react-router-dom'

const ScanResults = () => {
  const [selectedScan, setSelectedScan] = useState(null)
  const [scans] = useState([
    // Pour l'instant vide, sera rempli plus tard avec les vraies données
  ])

  const mockVulnerabilities = [
    {
      id: 1,
      title: 'Faille de sécurité critique',
      severity: 'critical',
      description: 'Une vulnérabilité critique a été détectée dans le système.',
      recommendation: 'Mettre à jour immédiatement le système vers la dernière version.',
      cve: 'CVE-2024-XXXX',
    },
    {
      id: 2,
      title: 'Configuration faible',
      severity: 'high',
      description: 'La configuration actuelle présente des faiblesses de sécurité.',
      recommendation: 'Renforcer la configuration selon les meilleures pratiques.',
      cve: null,
    },
  ]

  const severityColors = {
    critical: 'bg-red-500/20 text-red-400 border-red-500/50',
    high: 'bg-orange-500/20 text-orange-400 border-orange-500/50',
    medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
    low: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
    info: 'bg-gray-500/20 text-gray-400 border-gray-500/50',
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* En-tête */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">Résultats de Scan</h1>
          <p className="text-gray-400">Consultez les rapports de vulnérabilité</p>
        </div>
        <button className="btn-primary">
          📊 Nouveau scan
        </button>
      </div>

      {scans.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Liste des scans */}
          <div className="lg:col-span-1">
            <div className="card p-6">
              <h2 className="text-xl font-bold text-white mb-4">Scans récents</h2>
              <div className="space-y-2">
                {scans.map((scan) => (
                  <button
                    key={scan.id}
                    onClick={() => setSelectedScan(scan)}
                    className={`w-full text-left p-4 rounded-lg transition-colors ${
                      selectedScan?.id === scan.id
                        ? 'bg-primary-500/20 border border-primary-500/50'
                        : 'bg-dark-700/50 border border-dark-600 hover:bg-dark-700'
                    }`}
                  >
                    <div className="font-semibold text-white">{scan.name}</div>
                    <div className="text-sm text-gray-400 mt-1">{scan.date}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Détails du scan */}
          <div className="lg:col-span-2">
            {selectedScan && (
              <div className="card p-6">
                <h2 className="text-2xl font-bold text-white mb-6">{selectedScan.name}</h2>
                {/* Contenu du scan sélectionné */}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* État vide avec exemple */}
          <div className="lg:col-span-1">
            <div className="card p-6">
              <h2 className="text-xl font-bold text-white mb-4">Scans récents</h2>
              <div className="text-center py-8">
                <span className="text-4xl mb-4 block">📋</span>
                <p className="text-gray-400 text-sm">Aucun scan disponible</p>
              </div>
            </div>
          </div>

          <div className="lg:col-span-2">
            <div className="card p-6">
              <div className="text-center py-12">
                <span className="text-6xl mb-4 block">🔍</span>
                <h2 className="text-2xl font-bold text-white mb-2">Aucun scan effectué</h2>
                <p className="text-gray-400 mb-6">
                  Configurez un serveur et lancez votre premier scan pour voir les résultats ici.
                </p>
                <div className="flex justify-center space-x-4">
                  <Link to="/server-config" className="btn-primary">
                    Configurer un serveur
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Exemple de vulnérabilités (pour démo) */}
      <div className="card p-6">
        <h2 className="text-2xl font-bold text-white mb-6">Exemple de vulnérabilités détectées</h2>
        <div className="space-y-4">
          {mockVulnerabilities.map((vuln) => (
            <div
              key={vuln.id}
              className="p-6 bg-dark-700/30 rounded-lg border border-dark-600"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-white">{vuln.title}</h3>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium border ${severityColors[vuln.severity]}`}
                    >
                      {vuln.severity.toUpperCase()}
                    </span>
                    {vuln.cve && (
                      <span className="text-xs text-gray-400 font-mono bg-dark-800 px-2 py-1 rounded">
                        {vuln.cve}
                      </span>
                    )}
                  </div>
                  <p className="text-gray-300 mb-4">{vuln.description}</p>
                </div>
              </div>
              <div className="bg-primary-900/20 border border-primary-700/50 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-primary-300 mb-2">💡 Recommandation</h4>
                <p className="text-sm text-gray-300">{vuln.recommendation}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ScanResults
