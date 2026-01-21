# CAESAR - Backend API

Backend sécurisé pour l'application CAESAR avec authentification JWT et MongoDB.

## 🚀 Installation

1. **Installer les dépendances**
```bash
cd web/backend
npm install
```

2. **Configurer les variables d'environnement**
```bash
cp .env.example .env
```

Puis éditez le fichier `.env` et configurez :
- `MONGODB_URI` : URL de connexion MongoDB
- `JWT_SECRET` : Secret pour signer les tokens JWT (changez-le !)
- `PORT` : Port du serveur (défaut: 5000)
- `FRONTEND_URL` : URL du frontend pour CORS

3. **Démarrer le serveur**
```bash
npm run dev
```

Le serveur sera accessible sur `http://localhost:5000`

## 📡 Endpoints API

### Authentification

#### POST `/api/auth/register`
Inscription d'un nouvel utilisateur

**Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "MotDePasse123"
}
```

**Réponse (201):**
```json
{
  "success": true,
  "message": "Compte créé avec succès",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "...",
      "name": "John Doe",
      "email": "john@example.com"
    }
  }
}
```

#### POST `/api/auth/login`
Connexion d'un utilisateur

**Body:**
```json
{
  "email": "john@example.com",
  "password": "MotDePasse123"
}
```

**Réponse (200):**
```json
{
  "success": true,
  "message": "Connexion réussie",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "...",
      "name": "John Doe",
      "email": "john@example.com"
    }
  }
}
```

**Erreur (401):**
```json
{
  "success": false,
  "message": "Adresse email ou mot de passe incorrect"
}
```

#### GET `/api/auth/me`
Récupérer les informations de l'utilisateur connecté

**Headers:**
```
Authorization: Bearer <token>
```

**Réponse (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "...",
      "name": "John Doe",
      "email": "john@example.com"
    }
  }
}
```

## 🔒 Sécurité

- **Mots de passe hashés** avec bcrypt (10 rounds)
- **Tokens JWT** pour l'authentification
- **Validation des données** avec express-validator
- **CORS** configuré pour le frontend
- **Variables d'environnement** pour les secrets

## 🗄️ Base de données

Le projet utilise **MongoDB** avec **Mongoose**.

### Modèle User
- `name`: String (requis)
- `email`: String (requis, unique, validé)
- `password`: String (requis, min 8 caractères, hashé)
- `createdAt`: Date (automatique)
- `updatedAt`: Date (automatique)

## 📦 Technologies

- **Express.js** - Framework web
- **MongoDB + Mongoose** - Base de données
- **JWT** - Authentification
- **bcryptjs** - Hashage des mots de passe
- **express-validator** - Validation
- **CORS** - Partage de ressources cross-origin
- **dotenv** - Variables d'environnement
