import axios from 'axios'
import { config } from '@/config'

export const api = axios.create({
  baseURL: `${config.apiBaseUrl}/api/v1`,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Intercepteur pour gérer les erreurs
api.interceptors.response.use(
  response => response,
  error => {
    // Gestion globale des erreurs
    console.error('API Error:', error)
    return Promise.reject(error)
  }
) 