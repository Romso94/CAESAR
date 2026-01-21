# ⚡ Démarrage Rapide - Backend CAESAR

## 🚀 Installation en 3 étapes

### 1. Installer les dépendances du backend
```bash
cd web/backend
npm install
```

### 2. Configurer MongoDB

**Option A : MongoDB Atlas (Recommandé)**
1. Créer un compte gratuit sur [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Créer un cluster gratuit
3. Récupérer l'URI de connexion

**Option B : MongoDB Local**
- Installer MongoDB sur votre machine
- Utiliser : `mongodb://localhost:27017/caesar`

### 3. Créer le fichier .env

Dans `web/backend/`, créer un fichier `.env` :

```env
MONGODB_URI=mongodb://localhost:27017/caesar
# OU pour Atlas :
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/caesar

JWT_SECRET=changez_moi_avec_une_chaine_aleatoire_securisee
PORT=5000
FRONTEND_URL=http://localhost:3000
```

⚠️ **IMPORTANT** : Changez `JWT_SECRET` par une chaîne aléatoire sécurisée !

---

## ▶️ Démarrer l'application

### Terminal 1 - Backend
```bash
cd web/backend
npm run dev
```
✅ Backend sur `http://localhost:5000`

### Terminal 2 - Frontend
```bash
cd web/frontend
npm run dev
```
✅ Frontend sur `http://localhost:3000`

---

## 🧪 Tester

1. Aller sur `http://localhost:3000/register`
2. Créer un compte
3. Se connecter avec ce compte
4. ✅ Ça fonctionne !

---

## 📚 Documentation Complète

Voir `GUIDE_BACKEND.md` pour tous les détails.

---

## 🐛 Problèmes ?

### MongoDB ne se connecte pas
- Vérifier que MongoDB est démarré
- Vérifier l'URI dans `.env`
- Vérifier les credentials MongoDB Atlas

### Erreur CORS
- Vérifier `FRONTEND_URL` dans `.env`
- Vérifier que le frontend tourne sur le port 3000

### Token invalide
- Vérifier que `JWT_SECRET` est défini dans `.env`
- Vérifier que le token n'a pas expiré
