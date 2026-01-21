import mongoose from 'mongoose'

/**
 * Connexion à MongoDB
 * Cette fonction établit la connexion avec la base de données MongoDB
 */
const connectDB = async () => {
  try {
    const conn = await mongoose.connect(process.env.MONGODB_URI)
    console.log(`✅ MongoDB connecté : ${conn.connection.host}`)
  } catch (error) {
    console.error(`❌ Erreur de connexion MongoDB : ${error.message}`)
    process.exit(1) // Arrête le serveur si la connexion échoue
  }
}

export default connectDB
