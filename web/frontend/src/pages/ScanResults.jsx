import { useState } from 'react'
import { Link } from 'react-router-dom'

const ScanResults = () => {
  // Scan d'exemple réaliste
  const exampleScan = {
    id: 1,
    name: 'Scan Serveur Production - 192.168.1.100',
    date: '15 janvier 2025, 14:32',
    server: {
      name: 'Serveur Production',
      ip: '192.168.1.100',
      hostname: 'prod-server-01',
      os: 'Ubuntu 22.04 LTS',
      type: 'SSH',
    },
    scanDuration: '2h 34min',
    totalVulnerabilities: 12,
    stats: {
      critical: 2,
      high: 4,
      medium: 4,
      low: 2,
      info: 0,
    },
  }

  const [selectedScan, setSelectedScan] = useState(exampleScan)
  const [scans] = useState([exampleScan])

  const mockVulnerabilities = [
    {
      id: 1,
      title: 'Apache HTTP Server - Remote Code Execution (CVE-2023-43622)',
      severity: 'critical',
      description: 'Une vulnérabilité critique de type Remote Code Execution (RCE) a été détectée dans Apache HTTP Server version 2.4.57. Cette faille permet à un attaquant distant d\'exécuter du code arbitraire sur le serveur en exploitant une corruption mémoire dans le module mod_proxy_uwsgi.',
      recommendation: 'Mettre à jour immédiatement Apache HTTP Server vers la version 2.4.58 ou supérieure. Appliquer le correctif de sécurité dès que possible. En attendant la mise à jour, désactiver le module mod_proxy_uwsgi si non essentiel.',
      cve: 'CVE-2023-43622',
      cvss: '9.8',
      affected: 'Apache HTTP Server 2.4.0 - 2.4.57',
      port: 80,
      service: 'HTTP',
    },
    {
      id: 2,
      title: 'OpenSSH - Weak Key Exchange Algorithms',
      severity: 'critical',
      description: 'Le serveur SSH utilise des algorithmes d\'échange de clés obsolètes et vulnérables (diffie-hellman-group1-sha1, diffie-hellman-group14-sha1). Ces algorithmes sont considérés comme faibles et peuvent être exploités par des attaquants pour déchiffrer les communications.',
      recommendation: 'Configurer OpenSSH pour utiliser uniquement des algorithmes modernes et sécurisés. Modifier /etc/ssh/sshd_config pour désactiver les algorithmes SHA1 et utiliser uniquement SHA2/SHA3. Redémarrer le service SSH après modification.',
      cve: null,
      cvss: '7.5',
      affected: 'OpenSSH 7.4 - 8.9',
      port: 22,
      service: 'SSH',
    },
    {
      id: 3,
      title: 'MySQL Server - SQL Injection via Prepared Statements (CVE-2023-21980)',
      severity: 'high',
      description: 'Une vulnérabilité d\'injection SQL a été identifiée dans MySQL Server version 8.0.32. Un attaquant authentifié peut exploiter cette faille pour exécuter des requêtes SQL arbitraires, potentiellement compromettant l\'intégrité et la confidentialité des données.',
      recommendation: 'Mettre à jour MySQL vers la version 8.0.33 ou supérieure. Réviser toutes les requêtes SQL préparées pour s\'assurer qu\'elles utilisent correctement les paramètres liés. Activer l\'audit SQL pour détecter les tentatives d\'injection.',
      cve: 'CVE-2023-21980',
      cvss: '8.8',
      affected: 'MySQL Server 8.0.0 - 8.0.32',
      port: 3306,
      service: 'MySQL',
    },
    {
      id: 4,
      title: 'Nginx - HTTP Request Smuggling (CVE-2023-44487)',
      severity: 'high',
      description: 'Le serveur Nginx est vulnérable à une attaque de type HTTP Request Smuggling. Cette vulnérabilité permet à un attaquant de contourner les contrôles de sécurité en injectant des requêtes HTTP malformées qui sont interprétées différemment par le serveur et les proxies.',
      recommendation: 'Mettre à jour Nginx vers la version 1.25.3 ou supérieure. Configurer les limites de taille de requête HTTP. Implémenter un WAF (Web Application Firewall) pour filtrer les requêtes malformées.',
      cve: 'CVE-2023-44487',
      cvss: '7.5',
      affected: 'Nginx 1.25.0 - 1.25.2',
      port: 443,
      service: 'HTTPS',
    },
    {
      id: 5,
      title: 'Weak SSL/TLS Configuration',
      severity: 'high',
      description: 'Le serveur accepte des protocoles SSL/TLS obsolètes (SSLv3, TLS 1.0, TLS 1.1) et des suites de chiffrement faibles (RC4, DES, 3DES). Ces configurations permettent des attaques de type downgrade et man-in-the-middle.',
      recommendation: 'Désactiver SSLv3, TLS 1.0 et TLS 1.1. Configurer le serveur pour n\'accepter que TLS 1.2 et TLS 1.3. Désactiver les suites de chiffrement faibles. Utiliser uniquement des algorithmes modernes (AES-GCM, ChaCha20-Poly1305).',
      cve: null,
      cvss: '7.4',
      affected: 'Configuration serveur',
      port: 443,
      service: 'HTTPS',
    },
    {
      id: 6,
      title: 'Exposed Sensitive Files (.env, .git)',
      severity: 'high',
      description: 'Des fichiers sensibles sont accessibles publiquement via le serveur web. Les fichiers .env, .git/config et backup.sql sont accessibles sans authentification, exposant des informations d\'identification et des secrets d\'application.',
      recommendation: 'Supprimer ou déplacer les fichiers sensibles hors du répertoire web public. Configurer le serveur web pour refuser l\'accès aux fichiers commençant par un point. Implémenter un fichier .htaccess ou équivalent pour bloquer l\'accès aux fichiers sensibles.',
      cve: null,
      cvss: '7.5',
      affected: 'Application web',
      port: 80,
      service: 'HTTP',
    },
    {
      id: 7,
      title: 'PHP - Remote Code Execution (CVE-2023-3823)',
      severity: 'medium',
      description: 'Une vulnérabilité de type Remote Code Execution a été détectée dans PHP version 8.0.30. Cette faille peut être exploitée via des fonctions de désérialisation non sécurisées, permettant l\'exécution de code arbitraire.',
      recommendation: 'Mettre à jour PHP vers la version 8.0.30 (correctif) ou 8.1.22+. Désactiver les fonctions de désérialisation non essentielles. Utiliser des alternatives sécurisées comme JSON pour la sérialisation.',
      cve: 'CVE-2023-3823',
      cvss: '6.5',
      affected: 'PHP 8.0.0 - 8.0.29',
      port: 80,
      service: 'HTTP',
    },
    {
      id: 8,
      title: 'Weak Password Policy',
      severity: 'medium',
      description: 'Le serveur n\'impose pas de politique de mots de passe robuste. Les utilisateurs peuvent utiliser des mots de passe courts, simples et sans complexité. Plusieurs comptes utilisent des mots de passe par défaut ou facilement devinables.',
      recommendation: 'Implémenter une politique de mots de passe stricte : minimum 12 caractères, mélange de majuscules/minuscules, chiffres et caractères spéciaux. Forcer le changement de mot de passe tous les 90 jours. Activer l\'authentification à deux facteurs (2FA) pour les comptes privilégiés.',
      cve: null,
      cvss: '5.3',
      affected: 'Système d\'authentification',
      port: null,
      service: 'Système',
    },
    {
      id: 9,
      title: 'Missing Security Headers',
      severity: 'medium',
      description: 'Le serveur web ne renvoie pas les en-têtes de sécurité recommandés (Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, Strict-Transport-Security). Cela expose l\'application à des attaques XSS, clickjacking et MIME-sniffing.',
      recommendation: 'Configurer les en-têtes de sécurité HTTP : Content-Security-Policy, X-Frame-Options: DENY, X-Content-Type-Options: nosniff, Strict-Transport-Security avec max-age approprié. Utiliser un outil comme SecurityHeaders.com pour valider la configuration.',
      cve: null,
      cvss: '5.4',
      affected: 'Configuration serveur web',
      port: 80,
      service: 'HTTP',
    },
    {
      id: 10,
      title: 'Outdated System Packages',
      severity: 'medium',
      description: 'Plusieurs packages système sont obsolètes et contiennent des vulnérabilités connues. Les packages libssl3, openssh-client et curl n\'ont pas été mis à jour depuis plus de 6 mois, exposant le système à des failles de sécurité.',
      recommendation: 'Exécuter apt update && apt upgrade pour mettre à jour tous les packages système. Configurer des mises à jour automatiques pour les correctifs de sécurité. Surveiller les notifications de sécurité pour les packages critiques.',
      cve: null,
      cvss: '5.5',
      affected: 'Système d\'exploitation',
      port: null,
      service: 'Système',
    },
    {
      id: 11,
      title: 'Verbose Error Messages',
      severity: 'low',
      description: 'Le serveur renvoie des messages d\'erreur trop détaillés qui révèlent des informations sensibles sur la structure de l\'application, les versions de logiciels et les chemins de fichiers. Ces informations peuvent aider un attaquant à préparer une attaque.',
      recommendation: 'Configurer le serveur pour afficher des messages d\'erreur génériques en production. Désactiver l\'affichage des stack traces. Logger les erreurs détaillées dans des fichiers sécurisés accessibles uniquement aux administrateurs.',
      cve: null,
      cvss: '3.1',
      affected: 'Application web',
      port: 80,
      service: 'HTTP',
    },
    {
      id: 12,
      title: 'Unnecessary Services Running',
      severity: 'low',
      description: 'Plusieurs services non essentiels sont actifs sur le serveur (FTP, Telnet, SNMP). Ces services augmentent la surface d\'attaque et peuvent être exploités si mal configurés ou non mis à jour.',
      recommendation: 'Désactiver ou supprimer les services non utilisés. Si nécessaire, configurer des règles de pare-feu strictes pour limiter l\'accès à ces services. Utiliser uniquement des protocoles sécurisés (SFTP au lieu de FTP, SSH au lieu de Telnet).',
      cve: null,
      cvss: '3.7',
      affected: 'Services système',
      port: '21, 23, 161',
      service: 'FTP, Telnet, SNMP',
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
                    <div className="text-xs text-gray-500 mt-1">
                      {scan.totalVulnerabilities} vulnérabilité{scan.totalVulnerabilities > 1 ? 's' : ''}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Détails du scan */}
          <div className="lg:col-span-2 space-y-6">
            {selectedScan && (
              <>
                {/* En-tête du scan */}
                <div className="card p-6">
                  <div className="flex items-start justify-between mb-6">
                    <div>
                      <h2 className="text-2xl font-bold text-white mb-2">{selectedScan.name}</h2>
                      <p className="text-gray-400">Scan effectué le {selectedScan.date}</p>
                    </div>
                    <span className="px-3 py-1 bg-red-500/20 text-red-400 border border-red-500/50 rounded-full text-sm font-medium">
                      {selectedScan.stats.critical} Critique{selectedScan.stats.critical > 1 ? 's' : ''}
                    </span>
                  </div>

                  {/* Informations serveur */}
                  <div className="grid grid-cols-2 gap-4 mb-6 p-4 bg-dark-700/30 rounded-lg">
                    <div>
                      <p className="text-sm text-gray-400">Serveur</p>
                      <p className="text-white font-medium">{selectedScan.server.name}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Adresse IP</p>
                      <p className="text-white font-medium">{selectedScan.server.ip}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Système d'exploitation</p>
                      <p className="text-white font-medium">{selectedScan.server.os}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Durée du scan</p>
                      <p className="text-white font-medium">{selectedScan.scanDuration}</p>
                    </div>
                  </div>

                  {/* Statistiques */}
                  <div className="grid grid-cols-5 gap-3">
                    <div className="text-center p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                      <div className="text-2xl font-bold text-red-400">{selectedScan.stats.critical}</div>
                      <div className="text-xs text-gray-400 mt-1">Critique</div>
                    </div>
                    <div className="text-center p-3 bg-orange-500/10 border border-orange-500/30 rounded-lg">
                      <div className="text-2xl font-bold text-orange-400">{selectedScan.stats.high}</div>
                      <div className="text-xs text-gray-400 mt-1">Élevée</div>
                    </div>
                    <div className="text-center p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                      <div className="text-2xl font-bold text-yellow-400">{selectedScan.stats.medium}</div>
                      <div className="text-xs text-gray-400 mt-1">Moyenne</div>
                    </div>
                    <div className="text-center p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                      <div className="text-2xl font-bold text-blue-400">{selectedScan.stats.low}</div>
                      <div className="text-xs text-gray-400 mt-1">Faible</div>
                    </div>
                    <div className="text-center p-3 bg-gray-500/10 border border-gray-500/30 rounded-lg">
                      <div className="text-2xl font-bold text-gray-400">{selectedScan.totalVulnerabilities}</div>
                      <div className="text-xs text-gray-400 mt-1">Total</div>
                    </div>
                  </div>
                </div>

                {/* Résumé exécutif */}
                <div className="card p-6 bg-gradient-to-r from-red-900/20 to-orange-900/20 border-red-700/50">
                  <h3 className="text-xl font-bold text-white mb-3">📊 Résumé Exécutif</h3>
                  <p className="text-gray-300 leading-relaxed mb-4">
                    Le scan de sécurité a identifié <strong className="text-white">{selectedScan.totalVulnerabilities} vulnérabilités</strong> sur le serveur {selectedScan.server.name}. 
                    Parmi celles-ci, <strong className="text-red-400">{selectedScan.stats.critical} sont critiques</strong> et nécessitent une attention immédiate, 
                    <strong className="text-orange-400"> {selectedScan.stats.high} sont de niveau élevé</strong> et doivent être corrigées rapidement.
                  </p>
                  <p className="text-gray-300 leading-relaxed">
                    <strong className="text-white">Recommandation prioritaire :</strong> Corriger les vulnérabilités critiques dans les 24 heures. 
                    Les failles d'exécution de code à distance (RCE) et les configurations SSH faibles représentent un risque majeur pour la sécurité du système.
                  </p>
                </div>
              </>
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

      {/* Liste des vulnérabilités détaillées */}
      {selectedScan && (
        <div className="card p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white">Vulnérabilités Détectées</h2>
            <div className="text-sm text-gray-400">
              {mockVulnerabilities.length} vulnérabilité{mockVulnerabilities.length > 1 ? 's' : ''} trouvée{mockVulnerabilities.length > 1 ? 's' : ''}
            </div>
          </div>
          
          <div className="space-y-4">
            {mockVulnerabilities.map((vuln) => (
              <div
                key={vuln.id}
                className="p-6 bg-dark-700/30 rounded-lg border border-dark-600 hover:border-dark-500 transition-colors"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center flex-wrap gap-2 mb-3">
                      <h3 className="text-lg font-semibold text-white">{vuln.title}</h3>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium border ${severityColors[vuln.severity]}`}
                      >
                        {vuln.severity.toUpperCase()}
                      </span>
                      {vuln.cve && (
                        <span className="text-xs text-gray-300 font-mono bg-dark-800 px-2 py-1 rounded border border-dark-600">
                          {vuln.cve}
                        </span>
                      )}
                      {vuln.cvss && (
                        <span className="text-xs text-gray-400 bg-dark-800 px-2 py-1 rounded">
                          CVSS: {vuln.cvss}
                        </span>
                      )}
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                      {vuln.port && (
                        <div>
                          <span className="text-gray-400">Port/Service:</span>
                          <span className="text-white ml-2">{vuln.port} ({vuln.service})</span>
                        </div>
                      )}
                      {vuln.affected && (
                        <div>
                          <span className="text-gray-400">Affecté:</span>
                          <span className="text-white ml-2">{vuln.affected}</span>
                        </div>
                      )}
                    </div>
                    
                    <p className="text-gray-300 leading-relaxed mb-4">{vuln.description}</p>
                  </div>
                </div>
                
                <div className="bg-primary-900/20 border border-primary-700/50 rounded-lg p-4">
                  <h4 className="text-sm font-semibold text-primary-300 mb-2 flex items-center">
                    <span className="mr-2">💡</span>
                    Recommandation de Remédiation
                  </h4>
                  <p className="text-sm text-gray-300 leading-relaxed">{vuln.recommendation}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default ScanResults
