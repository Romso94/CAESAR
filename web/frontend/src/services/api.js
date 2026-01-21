/**
 * Service API - Gestion des appels au backend
 * 
 * Ce fichier centralise toutes les requêtes HTTP vers le backend
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

/**
 * Fonction utilitaire pour faire des requêtes HTTP
 */
const fetchAPI = async (endpoint, options = {}) => {
  const token = localStorage.getItem('caesar_token')
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    ...options,
  }

  // Si on envoie des données, les convertir en JSON
  if (options.body && typeof options.body === 'object') {
    config.body = JSON.stringify(options.body)
  }

  try {
    const response = await fetch(`${API_URL}${endpoint}`, config)
    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.message || 'Une erreur est survenue')
    }

    return data
  } catch (error) {
    throw error
  }
}

/**
 * Authentification
 */
export const authAPI = {
  // Inscription
  register: async (userData) => {
    return fetchAPI('/auth/register', {
      method: 'POST',
      body: userData,
    })
  },

  // Connexion
  login: async (email, password) => {
    return fetchAPI('/auth/login', {
      method: 'POST',
      body: { email, password },
    })
  },

  // Récupérer les infos de l'utilisateur connecté
  getMe: async () => {
    return fetchAPI('/auth/me', {
      method: 'GET',
    })
  },

  // Lister tous les utilisateurs (pour visualisation)
  getUsers: async () => {
    return fetchAPI('/auth/users', {
      method: 'GET',
    })
  },
}
