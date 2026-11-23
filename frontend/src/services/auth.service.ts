import api, { publicApi } from './api'
import type { User, AuthTokens } from '@/types'

export const authService = {
  async login(email: string, password: string): Promise<AuthTokens> {
    const response = await publicApi.post('/auth/token/', { email, password })
    return response.data
  },

  async register(data: {
    email: string
    password: string
    first_name: string
    last_name: string
    phone: string
  }): Promise<User> {
    const response = await publicApi.post('/auth/register/', data)
    return response.data
  },

  async getProfile(): Promise<User> {
    const response = await api.get('/auth/profile/')
    return response.data
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await api.patch('/auth/profile/', data)
    return response.data
  },

  async forgotPassword(email: string, redirectUrl: string): Promise<void> {
    await publicApi.post('/auth/forgot-password/', { email, redirect_url: redirectUrl })
  },

  async resetPassword(uid: string, token: string, newPassword: string): Promise<void> {
    await publicApi.post('/auth/reset-password/', { uid, token, new_password: newPassword })
  },

  async verifyEmail(token: string): Promise<void> {
    await publicApi.get('/auth/verify-email/', { params: { token } })
  },

  async resendVerificationEmail(email: string): Promise<void> {
    await publicApi.post('/auth/resend-verification/', { email })
  }
}
