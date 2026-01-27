# CAESAR Agent

Agent de scan réseau pour le système CAESAR. Cet agent se connecte au serveur de contrôle via WebSocket et effectue des scans de sécurité automatiques.

## Configuration

L'agent se configure via des variables d'environnement :

### Variables requises

- `IP_INTERFACE` : Adresse IP de la machine/réseau cible à scanner (requis)

### Variables optionnelles

- `SERVER_HOST` : Adresse du serveur WebSocket (défaut: `host.docker.internal`)
- `WEBSOCKET_PORT` : Port du serveur WebSocket (défaut: `8765`)
- `WEBSOCKET_SCHEME` : Schéma de connexion `ws` ou `wss` (défaut: `ws`)
- `SCAN_INTERVAL` : Intervalle entre les scans en secondes (défaut: `300`)

## Déploiement local (même machine que le serveur)

```bash
# Avec Docker Compose
docker-compose up -d

# Ou avec variables d'environnement
IP_INTERFACE=192.168.1.0/24 docker-compose up -d
```

## Déploiement distant (machine différente du serveur)

### 1. Configuration des variables d'environnement

**Linux/Mac :**
```bash
export SERVER_HOST=192.168.1.132
export WEBSOCKET_PORT=8765
export WEBSOCKET_SCHEME=ws
export IP_INTERFACE=10.0.0.0/24
export SCAN_INTERVAL=300

docker-compose up -d
```

**Windows PowerShell :**
```powershell
$env:SERVER_HOST="192.168.1.132"
$env:WEBSOCKET_PORT="8765"
$env:WEBSOCKET_SCHEME="ws"
$env:IP_INTERFACE="10.0.0.0/24"
$env:SCAN_INTERVAL="300"

docker-compose up -d
```

### 2. Création d'un fichier .env (recommandé)

Créez un fichier `.env` dans le dossier `agents/` :

```env
SERVER_HOST=192.168.1.132
WEBSOCKET_PORT=8765
WEBSOCKET_SCHEME=ws
IP_INTERFACE=10.0.0.0/24
SCAN_INTERVAL=300
```

Puis lancez :
```bash
docker-compose up -d
```

### 3. Utilisation de wss:// (WebSocket sécurisé)

Si votre serveur utilise SSL/TLS :

```bash
export WEBSOCKET_SCHEME=wss
export SERVER_HOST=caesar-server.example.com
export WEBSOCKET_PORT=443
```

## Exemples d'utilisation

### Scanner un réseau local depuis une machine distante

```bash
# Sur la machine agent (ex: 10.0.0.50)
export SERVER_HOST=192.168.1.132  # IP du serveur CAESAR
export IP_INTERFACE=10.0.0.0/24   # Réseau local à scanner
docker-compose up -d
```

### Scanner une seule machine

```bash
export SERVER_HOST=192.168.1.132
export IP_INTERFACE=10.0.0.100    # Une seule IP
docker-compose up -d
```

### Scanner avec intervalle personnalisé

```bash
export SERVER_HOST=192.168.1.132
export IP_INTERFACE=10.0.0.0/24
export SCAN_INTERVAL=600          # Scan toutes les 10 minutes
docker-compose up -d
```

## Vérification du statut

```bash
# Voir les logs de l'agent
docker logs -f caesar-agent

# Vérifier la connexion
docker logs caesar-agent | grep "Connecté au serveur"
```

## Dépannage

### L'agent ne se connecte pas

1. Vérifiez que le serveur est accessible :
   ```bash
   telnet SERVER_HOST WEBSOCKET_PORT
   # ou
   nc -zv SERVER_HOST WEBSOCKET_PORT
   ```

2. Vérifiez les logs de l'agent :
   ```bash
   docker logs caesar-agent
   ```

3. Vérifiez les variables d'environnement :
   ```bash
   docker exec caesar-agent env | grep SERVER
   ```

### Erreur "IP_INTERFACE doit être définie"

Assurez-vous d'avoir défini la variable `IP_INTERFACE` :
```bash
export IP_INTERFACE=192.168.1.0/24
```

### Timeout de connexion

- Vérifiez les règles de pare-feu entre l'agent et le serveur
- Vérifiez que le port WebSocket (défaut: 8765) est ouvert
- Essayez de pinger le serveur depuis la machine agent

## Architecture

```
Machine Agent (10.0.0.50)          Machine Serveur (192.168.1.132)
┌─────────────────────┐            ┌────────────────────────┐
│  Agent CAESAR       │  WebSocket │  Serveur CAESAR        │
│  - Scan Nmap        │◄──────────►│  - Contrôle agents     │
│  - Détection vuln.  │   :8765    │  - Stockage résultats  │
│  - Recherche exploit│            │  - Interface web       │
└─────────────────────┘            └────────────────────────┘
         │                                    │
         ▼                                    ▼
  Réseau cible                          MongoDB
  (10.0.0.0/24)                         (Scans/Users)
```

## Sécurité

- **Permissions root** : L'agent a besoin de privilèges élevés pour les scans Nmap
- **Réseau** : Limitez l'accès au serveur WebSocket via pare-feu
- **SSL/TLS** : Utilisez `wss://` en production pour chiffrer les communications
- **Authentification** : Envisagez d'ajouter une authentification au niveau WebSocket

## Outils inclus

- **Nmap** : Scanner réseau et détection de services
- **NSE scripts** : Scripts de détection de vulnérabilités
- **Searchsploit** : Recherche d'exploits (si disponible)
