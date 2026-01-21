# 🚀 Guide Complet du Backend CAESAR

## 📋 Vue d'ensemble

J'ai créé un backend complet et sécurisé pour votre application CAESAR. Voici tout ce qui a été fait, étape par étape.

---

## 🎯 Ce qui a été implémenté

✅ **Base de données MongoDB** avec Mongoose  
✅ **Authentification sécurisée** avec JWT (JSON Web Tokens)  
✅ **Hashage des mots de passe** avec bcrypt  
✅ **Validation des données** avec express-validator  
✅ **API REST** pour l'inscription et la connexion  
✅ **Frontend connecté** au backend  
✅ **Gestion des erreurs** propre et sécurisée  

---

## 📁 Structure du Backend

```
web/backend/
├── config/
│   └── database.js          # Connexion à MongoDB
├── models/
│   └── User.js              # Modèle utilisateur (schéma base de données)
├── routes/
│   └── authRoutes.js        # Routes d'authentification (register, login)
├── middleware/
│   └── auth.js              # Middleware pour protéger les routes
├── utils/
│   └── generateToken.js     # Génération des tokens JWT
├── server.js                # Point d'entrée du serveur
├── package.json             # Dépendances
└── .env                     # Variables d'environnement (à créer)
```

---

## 🔧 Étape 1 : Configuration du Projet

### 1.1 Package.json
Créé avec toutes les dépendances nécessaires :
- **express** : Framework web pour Node.js
- **mongoose** : ODM pour MongoDB
- **bcryptjs** : Hashage des mots de passe
- **jsonwebtoken** : Génération et vérification des tokens JWT
- **dotenv** : Gestion des variables d'environnement
- **cors** : Autorisation des requêtes cross-origin
- **express-validator** : Validation des données

### 1.2 Variables d'environnement
Le fichier `.env` contient :
- `MONGODB_URI` : URL de connexion à MongoDB
- `JWT_SECRET` : Secret pour signer les tokens (⚠️ À changer en production)
- `PORT` : Port du serveur (5000)
- `FRONTEND_URL` : URL du frontend pour CORS

---

## 🗄️ Étape 2 : Base de Données (MongoDB)

### 2.1 Modèle User (`models/User.js`)

**Structure des données :**
```javascript
{
  name: "John Doe",           // Nom complet
  email: "john@example.com",  // Email (unique)
  password: "hashé...",        // Mot de passe hashé
  createdAt: Date,            // Date de création (automatique)
  updatedAt: Date             // Date de modification (automatique)
}
```

**Fonctionnalités :**
- ✅ Email unique dans la base
- ✅ Validation de l'email (format)
- ✅ Mot de passe hashé automatiquement avant sauvegarde
- ✅ Méthode `matchPassword()` pour comparer les mots de passe

**Sécurité :**
- Le mot de passe est hashé avec **bcrypt** (10 rounds)
- Le mot de passe n'est jamais retourné dans les requêtes (`select: false`)

### 2.2 Connexion (`config/database.js`)

Gère la connexion à MongoDB avec gestion d'erreurs.

---

## 🔐 Étape 3 : Authentification JWT

### 3.1 Génération de Token (`utils/generateToken.js`)

Quand un utilisateur s'inscrit ou se connecte :
1. Un token JWT est généré
2. Le token contient l'ID de l'utilisateur
3. Le token expire dans 30 jours
4. Le token est signé avec `JWT_SECRET`

### 3.2 Middleware d'Authentification (`middleware/auth.js`)

**Fonction `protect` :**
- Vérifie la présence du token dans les headers
- Valide le token JWT
- Récupère l'utilisateur depuis la base de données
- Ajoute l'utilisateur à `req.user` pour les routes suivantes

**Utilisation :**
```javascript
router.get('/protected-route', protect, (req, res) => {
  // req.user contient les infos de l'utilisateur connecté
})
```

---

## 🛣️ Étape 4 : Routes API

### 4.1 POST `/api/auth/register` - Inscription

**Ce qui se passe :**
1. ✅ Validation des données (nom, email, mot de passe)
2. ✅ Vérification que l'email n'existe pas déjà
3. ✅ Hashage automatique du mot de passe
4. ✅ Création de l'utilisateur dans la base
5. ✅ Génération d'un token JWT
6. ✅ Retour du token et des infos utilisateur

**Validation :**
- Nom : minimum 2 caractères
- Email : format valide
- Mot de passe : minimum 8 caractères, avec majuscule, minuscule et chiffre

**Réponse en cas de succès (201) :**
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

**Réponse en cas d'erreur (400) :**
```json
{
  "success": false,
  "message": "Cet email est déjà utilisé"
}
```

### 4.2 POST `/api/auth/login` - Connexion

**Ce qui se passe :**
1. ✅ Validation de l'email et du mot de passe
2. ✅ Recherche de l'utilisateur dans la base
3. ✅ Vérification du mot de passe avec bcrypt
4. ✅ Génération d'un token JWT
5. ✅ Retour du token et des infos utilisateur

**Réponse en cas de succès (200) :**
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

**Réponse en cas d'erreur (401) :**
```json
{
  "success": false,
  "message": "Adresse email ou mot de passe incorrect"
}
```

⚠️ **Sécurité** : Le message d'erreur est générique pour ne pas révéler si l'email existe ou non.

### 4.3 GET `/api/auth/me` - Profil utilisateur

Route protégée qui retourne les infos de l'utilisateur connecté.

**Headers requis :**
```
Authorization: Bearer <token>
```

---

## 🎨 Étape 5 : Frontend Connecté

### 5.1 Service API (`frontend/src/services/api.js`)

Fichier centralisé pour toutes les requêtes HTTP :
- Gestion automatique du token JWT dans les headers
- Gestion des erreurs
- Formatage des requêtes

**Fonctions disponibles :**
- `authAPI.register(userData)` : Inscription
- `authAPI.login(email, password)` : Connexion
- `authAPI.getMe()` : Récupérer le profil (nécessite token)

### 5.2 Pages Modifiées

**Register.jsx :**
- ✅ Appel API lors de l'inscription
- ✅ Sauvegarde du token dans localStorage
- ✅ Gestion des erreurs du backend
- ✅ Indicateur de chargement

**Login.jsx :**
- ✅ Appel API lors de la connexion
- ✅ Message d'erreur si email/mot de passe incorrect
- ✅ Sauvegarde du token
- ✅ Indicateur de chargement

**App.jsx :**
- ✅ Vérification du token au chargement
- ✅ Validation du token avec l'API
- ✅ Nettoyage si token invalide

---

## 🔒 Sécurité Implémentée

### ✅ Mots de passe
- Hashés avec **bcrypt** (10 rounds)
- Jamais stockés en clair
- Jamais retournés dans les réponses API

### ✅ Tokens JWT
- Signés avec un secret
- Expirent après 30 jours
- Validés à chaque requête protégée

### ✅ Validation
- Validation côté serveur (express-validator)
- Validation côté client (double sécurité)
- Messages d'erreur sécurisés (ne révèlent pas si l'email existe)

### ✅ CORS
- Configuré pour autoriser uniquement le frontend
- Protection contre les requêtes non autorisées

### ✅ Gestion des erreurs
- Messages d'erreur clairs pour l'utilisateur
- Logs détaillés côté serveur
- Pas d'exposition d'informations sensibles

---

## 🚀 Installation et Démarrage

### 1. Installer MongoDB

**Option A : MongoDB Atlas (Recommandé - Gratuit)**
1. Créer un compte sur [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Créer un cluster gratuit
3. Récupérer l'URI de connexion

**Option B : MongoDB Local**
1. Installer MongoDB sur votre machine
2. Démarrer MongoDB
3. Utiliser `mongodb://localhost:27017/caesar`

### 2. Configurer le Backend

```bash
cd web/backend
npm install
```

Créer le fichier `.env` :
```bash
# Copier le fichier d'exemple
cp env.example.txt .env
```

Éditer `.env` :
```env
MONGODB_URI=mongodb://localhost:27017/caesar
# OU pour MongoDB Atlas :
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/caesar

JWT_SECRET=votre_secret_tres_securise_changez_moi
PORT=5000
FRONTEND_URL=http://localhost:3000
```

### 3. Démarrer le Backend

```bash
npm run dev
```

Le serveur démarre sur `http://localhost:5000`

### 4. Démarrer le Frontend

Dans un autre terminal :
```bash
cd web/frontend
npm run dev
```

Le frontend démarre sur `http://localhost:3000`

---

## 🧪 Tester l'Application

### Test d'inscription
1. Aller sur `http://localhost:3000/register`
2. Remplir le formulaire
3. Cliquer sur "Créer mon compte"
4. ✅ Vous devriez être redirigé vers le dashboard

### Test de connexion
1. Aller sur `http://localhost:3000/login`
2. Entrer l'email et le mot de passe
3. Cliquer sur "Se connecter"
4. ✅ Vous devriez être connecté

### Test d'erreur
1. Essayer de se connecter avec un email qui n'existe pas
2. ✅ Message : "Adresse email ou mot de passe incorrect"

---

## 📊 Flux d'Authentification

```
┌─────────┐                    ┌──────────┐                    ┌──────────┐
│Frontend │                    │ Backend  │                    │ MongoDB  │
└────┬────┘                    └────┬─────┘                    └────┬─────┘
     │                              │                              │
     │  1. POST /register           │                              │
     │  {name, email, password}     │                              │
     ├─────────────────────────────>│                              │
     │                              │  2. Vérifier email unique   │
     │                              ├─────────────────────────────>│
     │                              │<─────────────────────────────┤
     │                              │  3. Hasher le mot de passe   │
     │                              │  4. Créer l'utilisateur      │
     │                              ├─────────────────────────────>│
     │                              │<─────────────────────────────┤
     │                              │  5. Générer token JWT        │
     │  6. {token, user}            │                              │
     │<─────────────────────────────┤                              │
     │  7. Sauvegarder token        │                              │
     │     dans localStorage        │                              │
     │                              │                              │
```

---

## 🎓 Explications Techniques

### Pourquoi JWT ?
- **Stateless** : Pas besoin de stocker les sessions côté serveur
- **Scalable** : Fonctionne avec plusieurs serveurs
- **Sécurisé** : Signé et vérifiable

### Pourquoi bcrypt ?
- **Lent intentionnellement** : Résistant aux attaques brute-force
- **Salt automatique** : Chaque hash est unique
- **Standard de l'industrie** : Utilisé partout

### Pourquoi express-validator ?
- **Validation centralisée** : Toute la logique au même endroit
- **Messages d'erreur clairs** : Facile à comprendre
- **Sécurité** : Protection contre les injections

---

## 🐛 Dépannage

### Erreur : "MongoDB connecté" mais erreur de connexion
- Vérifier que MongoDB est démarré
- Vérifier l'URI dans `.env`
- Vérifier les credentials MongoDB Atlas

### Erreur : "Token invalide"
- Vérifier que `JWT_SECRET` est le même partout
- Vérifier que le token n'a pas expiré
- Vérifier le format du header : `Authorization: Bearer <token>`

### Erreur CORS
- Vérifier `FRONTEND_URL` dans `.env`
- Vérifier que le frontend tourne sur le bon port

---

## 📝 Prochaines Étapes Possibles

- [ ] Ajouter la réinitialisation de mot de passe
- [ ] Ajouter la vérification d'email
- [ ] Ajouter le refresh token
- [ ] Ajouter la gestion des rôles (admin, user)
- [ ] Ajouter la limitation de taux (rate limiting)
- [ ] Ajouter les logs d'audit

---

## ✅ Résumé

Vous avez maintenant :
- ✅ Un backend complet et sécurisé
- ✅ Une base de données MongoDB fonctionnelle
- ✅ Une authentification JWT
- ✅ Un frontend connecté au backend
- ✅ Des mots de passe hashés
- ✅ Des validations complètes
- ✅ Une gestion d'erreurs propre

**Tout est prêt à être utilisé ! 🎉**
