import api, { publicApi, sessionApi, csrfHeaders, withSessionLock } from './api'
import type { User, AuthTokens } from '@/types'

export const authService = {
  async login(email: string, password: string): Promise<AuthTokens> {
    return withSessionLock(async () => {
      const response = await sessionApi.post('/auth/token/', { email, password }, { headers: await csrfHeaders() })
      return response.data
    })
  },

  async logout(): Promise<void> {
    await withSessionLock(async () => { await sessionApi.post('/auth/logout/', {}, { headers: await csrfHeaders() }) })
  },

  async register(data: {
    email: string
    password?: string
    first_name: string
    last_name: string
    phone: string
  }): Promise<User> {
    const response = await publicApi.post('/auth/register/', data)
    return response.data
  },

  async completeSignup(setupToken: string, password: string): Promise<AuthTokens> {
    return withSessionLock(async () => {
      const response = await sessionApi.post(
        '/auth/complete-signup/',
        { setup_token: setupToken, password },
        { headers: await csrfHeaders() }
      )
      return response.data
    })
  },

  async googleLogin(credential: string): Promise<AuthTokens> {
    return withSessionLock(async () => {
      const response = await sessionApi.post(
        '/auth/google/',
        { credential },
        { headers: await csrfHeaders() }
      )
      return response.data
    })
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

  async verifyEmail(email: string, code: string): Promise<{ detail?: string; requires_password?: boolean; setup_token?: string } | void> {
    const response = await publicApi.post('/auth/verify-email/', { email, code })
    return response.data
  },

  async resendVerificationEmail(email: string): Promise<void> {
    await publicApi.post('/auth/resend-verification/', { email })
  }
}
