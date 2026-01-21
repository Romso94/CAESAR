import express from 'express'
import dotenv from 'dotenv'
import cors from 'cors'
import connectDB from './config/database.js'
import authRoutes from './routes/authRoutes.js'

// Charger les variables d'environnement
dotenv.config()

// Connexion à la base de données
connectDB()

// Créer l'application Express
const app = express()

// Middleware
app.use(express.json()) // Permet de parser les requêtes JSON
app.use(express.urlencoded({ extended: true })) // Permet de parser les données de formulaire

// Configuration CORS (Cross-Origin Resource Sharing)
// Permet au frontend (port 3000) de communiquer avec le backend (port 5000)
app.use(
  cors({
    origin: process.env.FRONTEND_URL || 'http://localhost:3000',
    credentials: true,
  })
)

// Routes
app.use('/api/auth', authRoutes)

// Route de test
app.get('/api/health', (req, res) => {
  res.json({
    success: true,
    message: 'API CAESAR fonctionnelle',
    timestamp: new Date().toISOString(),
  })
})

// Gestion des routes non trouvées
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    message: 'Route non trouvée',
  })
})

// Gestion des erreurs globales
app.use((err, req, res, next) => {
  console.error('Erreur:', err)
  res.status(500).json({
    success: false,
    message: 'Erreur serveur',
    error: process.env.NODE_ENV === 'development' ? err.message : undefined,
  })
})

// Démarrer le serveur
const PORT = process.env.PORT || 5000
app.listen(PORT, () => {
  console.log(`🚀 Serveur démarré sur le port ${PORT}`)
  console.log(`📍 API disponible sur http://localhost:${PORT}/api`)
})
