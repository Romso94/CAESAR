import mongoose from 'mongoose'
import bcrypt from 'bcryptjs'

/**
 * Modèle User - Schéma de la base de données pour les utilisateurs
 * 
 * Ce modèle définit la structure des données utilisateur :
 * - name : Nom complet
 * - email : Email (unique, utilisé pour la connexion)
 * - password : Mot de passe (hashé avec bcrypt)
 * - createdAt : Date de création
 */
const userSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: [true, 'Le nom est requis'],
      trim: true, // Supprime les espaces en début/fin
    },
    email: {
      type: String,
      required: [true, "L'email est requis"],
      unique: true, // Email unique dans la base
      lowercase: true, // Convertit en minuscules
      trim: true,
      match: [
        /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/,
        'Veuillez entrer un email valide',
      ],
    },
    password: {
      type: String,
      required: [true, 'Le mot de passe est requis'],
      minlength: [8, 'Le mot de passe doit contenir au moins 8 caractères'],
      select: false, // Par défaut, ne pas retourner le mot de passe dans les requêtes
    },
  },
  {
    timestamps: true, // Ajoute automatiquement createdAt et updatedAt
  }
)

/**
 * Middleware Mongoose : Hash le mot de passe AVANT de sauvegarder
 * S'exécute automatiquement avant chaque sauvegarde
 */
userSchema.pre('save', async function (next) {
  // Si le mot de passe n'a pas été modifié, on passe
  if (!this.isModified('password')) {
    return next()
  }

  // Hash le mot de passe avec bcrypt (10 rounds = bon équilibre sécurité/performance)
  const salt = await bcrypt.genSalt(10)
  this.password = await bcrypt.hash(this.password, salt)
  next()
})

/**
 * Méthode pour comparer le mot de passe entré avec celui en base
 * Utilisée lors de la connexion
 */
userSchema.methods.matchPassword = async function (enteredPassword) {
  return await bcrypt.compare(enteredPassword, this.password)
}

// Créer et exporter le modèle
const User = mongoose.model('User', userSchema)

export default User
