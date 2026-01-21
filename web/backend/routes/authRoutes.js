import express from 'express'
import { body, validationResult } from 'express-validator'
import User from '../models/User.js'
import { generateToken } from '../utils/generateToken.js'
import { protect } from '../middleware/auth.js'

const router = express.Router()

/**
 * @route   POST /api/auth/register
 * @desc    Inscription d'un nouvel utilisateur
 * @access  Public
 */
router.post(
  '/register',
  [
    // Validation des données avec express-validator
    body('name')
      .trim()
      .notEmpty()
      .withMessage('Le nom est requis')
      .isLength({ min: 2 })
      .withMessage('Le nom doit contenir au moins 2 caractères'),
    body('email')
      .isEmail()
      .normalizeEmail()
      .withMessage('Veuillez entrer un email valide'),
    body('password')
      .isLength({ min: 8 })
      .withMessage('Le mot de passe doit contenir au moins 8 caractères'),
  ],
  async (req, res) => {
    try {
      // Vérifier les erreurs de validation
      const errors = validationResult(req)
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          message: 'Erreurs de validation',
          errors: errors.array(),
        })
      }

      const { name, email, password } = req.body

      // Vérifier si l'utilisateur existe déjà
      const userExists = await User.findOne({ email })
      if (userExists) {
        return res.status(400).json({
          success: false,
          message: 'Cet email est déjà utilisé',
        })
      }

      // Créer le nouvel utilisateur
      // Le mot de passe sera automatiquement hashé grâce au middleware pre('save')
      const user = await User.create({
        name,
        email,
        password, // Sera hashé automatiquement
      })

      // Générer le token JWT
      const token = generateToken(user._id)

      // Retourner les informations (sans le mot de passe)
      res.status(201).json({
        success: true,
        message: 'Compte créé avec succès',
        data: {
          token,
          user: {
            id: user._id,
            name: user.name,
            email: user.email,
          },
        },
      })
    } catch (error) {
      console.error('Erreur lors de l\'inscription:', error)
      res.status(500).json({
        success: false,
        message: 'Erreur serveur lors de l\'inscription',
      })
    }
  }
)

/**
 * @route   POST /api/auth/login
 * @desc    Connexion d'un utilisateur
 * @access  Public
 */
router.post(
  '/login',
  [
    // Validation
    body('email').isEmail().normalizeEmail().withMessage('Email invalide'),
    body('password').notEmpty().withMessage('Le mot de passe est requis'),
  ],
  async (req, res) => {
    try {
      // Vérifier les erreurs de validation
      const errors = validationResult(req)
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          message: 'Erreurs de validation',
          errors: errors.array(),
        })
      }

      const { email, password } = req.body

      // Trouver l'utilisateur ET récupérer le mot de passe (select: false par défaut)
      const user = await User.findOne({ email }).select('+password')

      // Vérifier si l'utilisateur existe
      if (!user) {
        return res.status(401).json({
          success: false,
          message: 'Adresse email ou mot de passe incorrect',
        })
      }

      // Vérifier le mot de passe
      const isPasswordMatch = await user.matchPassword(password)
      if (!isPasswordMatch) {
        return res.status(401).json({
          success: false,
          message: 'Adresse email ou mot de passe incorrect',
        })
      }

      // Générer le token JWT
      const token = generateToken(user._id)

      // Retourner les informations
      res.status(200).json({
        success: true,
        message: 'Connexion réussie',
        data: {
          token,
          user: {
            id: user._id,
            name: user.name,
            email: user.email,
          },
        },
      })
    } catch (error) {
      console.error('Erreur lors de la connexion:', error)
      res.status(500).json({
        success: false,
        message: 'Erreur serveur lors de la connexion',
      })
    }
  }
)

/**
 * @route   GET /api/auth/me
 * @desc    Récupérer les informations de l'utilisateur connecté
 * @access  Private (nécessite un token valide)
 */
router.get('/me', protect, async (req, res) => {
  try {
    // req.user est défini par le middleware protect
    res.status(200).json({
      success: true,
      data: {
        user: {
          id: req.user._id,
          name: req.user.name,
          email: req.user.email,
        },
      },
    })
  } catch (error) {
    console.error('Erreur lors de la récupération du profil:', error)
    res.status(500).json({
      success: false,
      message: 'Erreur serveur',
    })
  }
})

/**
 * @route   GET /api/auth/users
 * @desc    Lister tous les utilisateurs (pour visualisation)
 * @access  Private (nécessite un token valide)
 */
router.get('/users', protect, async (req, res) => {
  try {
    const users = await User.find({}).select('-password').sort({ createdAt: -1 })
    
    res.status(200).json({
      success: true,
      count: users.length,
      data: {
        users,
      },
    })
  } catch (error) {
    console.error('Erreur lors de la récupération des utilisateurs:', error)
    res.status(500).json({
      success: false,
      message: 'Erreur serveur',
    })
  }
})

export default router
