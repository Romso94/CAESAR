# CAESAR Server

Serveur FastAPI pour la gestion des agents de sécurité CAESAR.

## Démarrage avec Docker Compose

Le moyen le plus simple de démarrer le serveur est d'utiliser Docker Compose :

```bash
cd server
docker-compose up -d
```

Cela démarre :
- **MongoDB principal** (port 27017) : Base de données pour les utilisateurs
- **MongoDB scans** (port 27018) : Base de données pour stocker les résultats de scans
- **Serveur FastAPI** (port 8000) : API et interface web
- **Serveur WebSocket** (port 8765) : Communication avec les agents

## Configuration

Copiez `.env.example` vers `.env` et modifiez les variables selon vos besoins :

```bash
cp .env.example .env
```

**Important** : Changez `SECRET_KEY` par une clé secrète forte en production !

## Première utilisation

1. Accédez à `http://localhost:8000`
2. Cliquez sur "S'inscrire" pour créer un compte
3. Connectez-vous avec vos identifiants

## Bases de données MongoDB

### MongoDB Principal (caesar)
- **Collection `users`** : Stocke les utilisateurs avec leurs mots de passe hashés
- Utilisé pour l'authentification

### MongoDB Scans (caesar_scans)
- **Collection `scans`** : Stocke les résultats de scans des agents
- Contient les résultats Nmap, vulnérabilités et exploits

## Arrêt

```bash
docker-compose down
```

Pour supprimer aussi les volumes (données) :

```bash
docker-compose down -v
```
