import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '@/stores/user'
import { authService } from '@/services/auth.service'
import { sessionState } from '@/services/session'

describe('UserStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    sessionState.notice = null
  })
  afterEach(() => vi.restoreAllMocks())

  it('starts unauthenticated', () => {
    const store = useUserStore()
    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBeNull()
  })

  it('is not admin by default', () => {
    const store = useUserStore()
    expect(store.isAdmin).toBe(false)
  })

  it('uses server staff status rather than the display role', () => {
    const store = useUserStore()
    const user = { id: '1', email: 'a@example.com', first_name: '', last_name: '', phone: '', role: 'admin' as const, is_staff: false }
    store.user = user
    expect(store.isAdmin).toBe(false)
    store.user = { ...user, role: 'customer', is_staff: true }
    expect(store.isAdmin).toBe(true)
  })

  it('stores tokens in localStorage', () => {
    localStorage.setItem('access_token', 'test-access')
    localStorage.setItem('refresh_token', 'test-refresh')
    expect(localStorage.getItem('access_token')).toBe('test-access')
    expect(localStorage.getItem('refresh_token')).toBe('test-refresh')
  })

  it('clears user state on logout', () => {
    const store = useUserStore()
    store.logout()
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(localStorage.getItem('access_token')).toBeNull()
  })

  it('retains the signed-in identity and credentials when the profile service is unavailable', async () => {
    const store = useUserStore()
    store.user = { id: '1', email: 'a@example.com', first_name: '', last_name: '', phone: '', role: 'customer', is_staff: false }
    localStorage.setItem('access_token', 'access')
    localStorage.setItem('refresh_token', 'refresh')
    vi.spyOn(authService, 'getProfile').mockRejectedValue(new Error('network unavailable'))
    await expect(store.fetchProfile()).rejects.toThrow('network unavailable')
    expect(store.isAuthenticated).toBe(true)
    expect(localStorage.getItem('refresh_token')).toBe('refresh')
    expect(sessionState.notice).toBe('unavailable')
  })

  it('clears the displayed identity when the session expires', () => {
    const store = useUserStore()
    store.user = { id: '1', email: 'a@example.com', first_name: '', last_name: '', phone: '', role: 'customer', is_staff: false }
    window.dispatchEvent(new Event('bynzuri:session-expired'))
    expect(store.isAuthenticated).toBe(false)
  })
})
