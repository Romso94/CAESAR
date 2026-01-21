import jwt from 'jsonwebtoken'
import User from '../models/User.js'

/**
 * Middleware d'authentification
 * 
 * Vérifie que l'utilisateur est authentifié en validant le token JWT
 * Ajoute l'utilisateur à req.user si le token est valide
 */
export const protect = async (req, res, next) => {
  let token

  // Récupérer le token depuis les headers
  // Format attendu : Authorization: Bearer <token>
  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
    token = req.headers.authorization.split(' ')[1]
  }

  // Si pas de token, refuser l'accès
  if (!token) {
    return res.status(401).json({
      success: false,
      message: 'Non autorisé - Token manquant',
    })
  }

  try {
    // Vérifier et décoder le token
    const decoded = jwt.verify(token, process.env.JWT_SECRET)

    // Récupérer l'utilisateur depuis la base (sans le mot de passe)
    req.user = await User.findById(decoded.id).select('-password')

    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: 'Utilisateur introuvable',
      })
    }

    // Tout est OK, passer à la route suivante
    next()
  } catch (error) {
    return res.status(401).json({
      success: false,
      message: 'Token invalide ou expiré',
    })
  }
}
