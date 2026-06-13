import api from './api'
import type { User, AuthTokens } from '@/types'

export const authService = {
  async login(email: string, password: string): Promise<AuthTokens> {
    const response = await api.post('/auth/token/', { email, password })
    return response.data
  },

  async register(data: {
    email: string
    password: string
    first_name: string
    last_name: string
    phone: string
  }): Promise<User> {
    const response = await api.post('/auth/register/', data)
    return response.data
  },

  async getProfile(): Promise<User> {
    const response = await api.get('/auth/profile/')
    return response.data
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await api.patch('/auth/profile/', data)
    return response.data
  }
}
