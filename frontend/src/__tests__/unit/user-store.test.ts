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

  it('clears user state after the server confirms logout', async () => {
    vi.spyOn(authService, 'logout').mockResolvedValue()
    const store = useUserStore()
    expect(await store.logout()).toBe(true)
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(localStorage.getItem('access_token')).toBeNull()
  })

  it('exposes progress and retains the session when sign-out cannot be confirmed', async () => {
    const store = useUserStore()
    store.user = { id: '1', email: 'a@example.com', first_name: '', last_name: '', phone: '', role: 'customer', is_staff: false }
    setAccessToken('access')
    let rejectLogout!: (error: Error) => void
    vi.spyOn(authService, 'logout').mockImplementation(() => new Promise((_, reject) => { rejectLogout = reject }))
    const result = store.logout()
    expect(store.signingOut).toBe(true)
    expect(store.isAuthenticated).toBe(true)
    rejectLogout(new Error('offline'))
    expect(await result).toBe(false)
    expect(store.signingOut).toBe(false)
    expect(store.isAuthenticated).toBe(true)
    expect(getAccessToken()).toBe('access')
  })

  it('does not restore a profile response that arrives after sign-out', async () => {
    const store = useUserStore()
    setAccessToken('access')
    let completeProfile!: (user: NonNullable<typeof store.user>) => void
    vi.spyOn(authService, 'getProfile').mockImplementation(() => new Promise(resolve => { completeProfile = resolve }))
    vi.spyOn(authService, 'logout').mockResolvedValue()
    const pending = store.fetchProfile()
    await store.logout()
    completeProfile({ id: '1', email: 'a@example.com', first_name: '', last_name: '', phone: '', role: 'customer', is_staff: false })
    await pending
    expect(store.user).toBeNull()
    expect(getAccessToken()).toBeNull()
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
