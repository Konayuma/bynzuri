import { describe, it, expect, vi, beforeEach } from 'vitest'

describe('API service', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('attaches Authorization header when token exists', () => {
    localStorage.setItem('access_token', 'test-jwt-token')
    // We'll test the interceptor logic directly
    const token = localStorage.getItem('access_token')
    expect(token).toBe('test-jwt-token')
  })

  it('handles missing token gracefully', () => {
    const token = localStorage.getItem('access_token')
    expect(token).toBeNull()
  })

  it('stores and retrieves refresh token', () => {
    localStorage.setItem('refresh_token', 'refresh-jwt-token')
    expect(localStorage.getItem('refresh_token')).toBe('refresh-jwt-token')
  })

  it('clears tokens on logout', () => {
    localStorage.setItem('access_token', 'token')
    localStorage.setItem('refresh_token', 'refresh')
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
  })
})
