import jwt from 'jsonwebtoken'

/**
 * Génère un token JWT pour l'utilisateur
 * 
 * Le token contient l'ID de l'utilisateur et expire dans 30 jours
 * Utilisé après l'inscription ou la connexion
 */
export const generateToken = (userId) => {
  return jwt.sign({ id: userId }, process.env.JWT_SECRET, {
    expiresIn: '30d', // Le token expire dans 30 jours
  })
}
