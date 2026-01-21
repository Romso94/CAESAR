# 👀 Comment Visualiser votre Base de Données MongoDB

Il existe plusieurs méthodes pour voir les utilisateurs inscrits dans votre base de données. Voici les meilleures options :

---

## 🎯 Méthode 1 : Via l'Interface Web (Recommandé)

J'ai créé une page dans votre application pour visualiser les utilisateurs !

### Comment y accéder :
1. Connectez-vous à votre application (`http://localhost:3000/login`)
2. Allez dans l'onglet **"Utilisateurs"** dans la navigation
3. Vous verrez tous les utilisateurs inscrits avec :
   - Nom
   - Email
   - Date d'inscription

**URL directe :** `http://localhost:3000/users`

---

## 🖥️ Méthode 2 : MongoDB Compass (Interface Graphique)

**MongoDB Compass** est l'outil officiel de MongoDB pour visualiser et gérer votre base de données.

### Installation :
1. Téléchargez MongoDB Compass : https://www.mongodb.com/try/download/compass
2. Installez l'application

### Connexion :

**Si vous utilisez MongoDB Local :**
```
mongodb://localhost:27017
```

**Si vous utilisez MongoDB Atlas :**
1. Connectez-vous à votre cluster sur MongoDB Atlas
2. Cliquez sur "Connect" → "Connect using MongoDB Compass"
3. Copiez la chaîne de connexion
4. Collez-la dans MongoDB Compass

### Navigation :
1. Une fois connecté, vous verrez vos bases de données
2. Cliquez sur la base `caesar`
3. Cliquez sur la collection `users`
4. Vous verrez tous les utilisateurs avec leurs données

**Avantages :**
- ✅ Interface graphique intuitive
- ✅ Visualisation des données en format JSON
- ✅ Possibilité de modifier/supprimer des données
- ✅ Requêtes visuelles

---

## ☁️ Méthode 3 : MongoDB Atlas (Si vous utilisez Atlas)

Si vous utilisez MongoDB Atlas (cloud), vous pouvez visualiser directement depuis le navigateur :

1. Connectez-vous à https://cloud.mongodb.com
2. Sélectionnez votre cluster
3. Cliquez sur "Browse Collections"
4. Naviguez vers `caesar` → `users`
5. Vous verrez tous les utilisateurs

**Avantages :**
- ✅ Pas besoin d'installer quoi que ce soit
- ✅ Accessible depuis n'importe où
- ✅ Interface web moderne

---

## 💻 Méthode 4 : Ligne de Commande (MongoDB Shell)

Si vous avez MongoDB installé localement, vous pouvez utiliser le shell :

### Connexion :
```bash
mongosh
# ou
mongo
```

### Commandes utiles :
```javascript
// Lister les bases de données
show dbs

// Utiliser la base caesar
use caesar

// Lister les collections
show collections

// Voir tous les utilisateurs
db.users.find().pretty()

// Compter les utilisateurs
db.users.countDocuments()

// Voir un utilisateur spécifique
db.users.findOne({ email: "exemple@email.com" })
```

---

## 🔌 Méthode 5 : Via l'API REST

Vous pouvez aussi appeler directement l'API :

### Avec curl (ligne de commande) :
```bash
# D'abord, connectez-vous pour obtenir un token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"votre@email.com","password":"votre_mot_de_passe"}'

# Ensuite, utilisez le token pour lister les utilisateurs
curl -X GET http://localhost:5000/api/auth/users \
  -H "Authorization: Bearer VOTRE_TOKEN_ICI"
```

### Avec Postman ou Insomnia :
1. Créez une requête GET vers `http://localhost:5000/api/auth/users`
2. Dans les Headers, ajoutez :
   - Key: `Authorization`
   - Value: `Bearer VOTRE_TOKEN`
3. Envoyez la requête

---

## 📊 Structure des Données

Voici à quoi ressemble un utilisateur dans la base :

```json
{
  "_id": "507f1f77bcf86cd799439011",
  "name": "John Doe",
  "email": "john@example.com",
  "password": "$2a$10$hashed_password_here...",
  "createdAt": "2025-01-15T10:30:00.000Z",
  "updatedAt": "2025-01-15T10:30:00.000Z"
}
```

**Note :** Le mot de passe est hashé avec bcrypt, vous ne pouvez pas le voir en clair (c'est normal et sécurisé !)

---

## 🎯 Recommandation

Pour un usage quotidien, je recommande :
1. **MongoDB Compass** si vous voulez une interface complète
2. **La page Utilisateurs** dans votre app si vous voulez juste voir rapidement
3. **MongoDB Atlas** si vous utilisez déjà le cloud

---

## 🐛 Problèmes Courants

### "Cannot connect to MongoDB"
- Vérifiez que MongoDB est démarré
- Vérifiez l'URI dans votre `.env`
- Vérifiez les credentials MongoDB Atlas

### "Collection users not found"
- C'est normal si aucun utilisateur ne s'est encore inscrit
- La collection sera créée automatiquement au premier enregistrement

### "Access denied"
- Vérifiez que vous êtes connecté avec un token valide
- Vérifiez que le backend est démarré

---

## ✅ Résumé

Vous avez maintenant **5 méthodes** pour visualiser votre base de données :
1. ✅ Page web dans votre application (`/users`)
2. ✅ MongoDB Compass (interface graphique)
3. ✅ MongoDB Atlas (si cloud)
4. ✅ Ligne de commande (mongosh)
5. ✅ API REST (curl, Postman)

Choisissez celle qui vous convient le mieux ! 🚀
