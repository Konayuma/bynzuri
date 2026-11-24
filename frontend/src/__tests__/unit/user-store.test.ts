import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '@/stores/user'
import { authService } from '@/services/auth.service'
import { sessionState } from '@/services/session'
import { clearSession, getAccessToken, setAccessToken } from '@/services/api'

describe('UserStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    clearSession()
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

  it('keeps access tokens in memory rather than localStorage', () => {
    setAccessToken('test-access')
    expect(getAccessToken()).toBe('test-access')
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
  })

  it('clears user state on logout', () => {
    vi.spyOn(authService, 'logout').mockResolvedValue()
    const store = useUserStore()
    store.logout()
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(localStorage.getItem('access_token')).toBeNull()
  })

  it('retains the signed-in identity and credentials when the profile service is unavailable', async () => {
    const store = useUserStore()
    store.user = { id: '1', email: 'a@example.com', first_name: '', last_name: '', phone: '', role: 'customer', is_staff: false }
    setAccessToken('access')
    vi.spyOn(authService, 'getProfile').mockRejectedValue(new Error('network unavailable'))
    await expect(store.fetchProfile()).rejects.toThrow('network unavailable')
    expect(store.isAuthenticated).toBe(true)
    expect(getAccessToken()).toBe('access')
    expect(sessionState.notice).toBe('unavailable')
  })

  it('clears the displayed identity when the session expires', () => {
    const store = useUserStore()
    store.user = { id: '1', email: 'a@example.com', first_name: '', last_name: '', phone: '', role: 'customer', is_staff: false }
    window.dispatchEvent(new Event('bynzuri:session-expired'))
    expect(store.isAuthenticated).toBe(false)
  })
})
