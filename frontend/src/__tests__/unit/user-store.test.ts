import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '@/stores/user'

describe('UserStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('starts unauthenticated', () => {
    const store = useUserStore()
    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBeNull()
  })

  it('is not admin by default', () => {
    const store = useUserStore()
    expect(store.isAdmin).toBe(false)
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
})
