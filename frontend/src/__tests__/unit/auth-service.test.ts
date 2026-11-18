import { describe, it, expect, vi, beforeEach } from 'vitest'
import { authService } from '@/services/auth.service'
import api, { publicApi } from '@/services/api'

vi.mock('@/services/api', () => ({
  publicApi: { post: vi.fn() },
  default: {
    post: vi.fn(),
    get: vi.fn(),
    patch: vi.fn(),
  },
}))

describe('authService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('calls login endpoint', async () => {
    vi.mocked(publicApi.post).mockResolvedValue({ data: { access: 'token', refresh: 'refresh' } })
    const result = await authService.login('test@example.com', 'password123')
    expect(publicApi.post).toHaveBeenCalledWith('/auth/token/', { email: 'test@example.com', password: 'password123' })
    expect(result).toEqual({ access: 'token', refresh: 'refresh' })
  })

  it('calls register endpoint', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: { id: '1', email: 'test@example.com' } })
    await authService.register({
      email: 'test@example.com',
      password: 'password123',
      first_name: 'Test',
      last_name: 'User',
      phone: '260123456789',
    })
    expect(api.post).toHaveBeenCalledWith('/auth/register/', {
      email: 'test@example.com',
      password: 'password123',
      first_name: 'Test',
      last_name: 'User',
      phone: '260123456789',
    })
  })

  it('calls forgot password endpoint', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: {} })
    await authService.forgotPassword('test@example.com', 'https://bynzuri.com')
    expect(api.post).toHaveBeenCalledWith('/auth/forgot-password/', {
      email: 'test@example.com',
      redirect_url: 'https://bynzuri.com',
    })
  })

  it('calls reset password endpoint', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: {} })
    await authService.resetPassword('uid123', 'token123', 'newpassword')
    expect(api.post).toHaveBeenCalledWith('/auth/reset-password/', {
      uid: 'uid123',
      token: 'token123',
      new_password: 'newpassword',
    })
  })

  it('calls verify email endpoint', async () => {
    vi.mocked(api.get).mockResolvedValue({ data: {} })
    await authService.verifyEmail('token123')
    expect(api.get).toHaveBeenCalledWith('/auth/verify-email/', { params: { token: 'token123' } })
  })

  it('calls resend verification email endpoint', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: {} })
    await authService.resendVerificationEmail('test@example.com')
    expect(api.post).toHaveBeenCalledWith('/auth/resend-verification/', { email: 'test@example.com' })
  })

  it('calls get profile endpoint', async () => {
    vi.mocked(api.get).mockResolvedValue({ data: { id: '1', email: 'test@example.com' } })
    const result = await authService.getProfile()
    expect(api.get).toHaveBeenCalledWith('/auth/profile/')
    expect(result).toEqual({ id: '1', email: 'test@example.com' })
  })

  it('calls update profile endpoint', async () => {
    vi.mocked(api.patch).mockResolvedValue({ data: { id: '1', first_name: 'Updated' } })
    await authService.updateProfile({ first_name: 'Updated' })
    expect(api.patch).toHaveBeenCalledWith('/auth/profile/', { first_name: 'Updated' })
  })
})
