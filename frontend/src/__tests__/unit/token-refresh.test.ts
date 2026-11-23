import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import axios, { AxiosError, AxiosHeaders } from 'axios'
import api from '@/services/api'
import { sessionState } from '@/services/session'

const originalAdapter = api.defaults.adapter

describe('expired access tokens', () => {
  beforeEach(() => {
    localStorage.clear()
    sessionState.notice = null
    localStorage.setItem('access_token', 'expired')
    localStorage.setItem('refresh_token', 'old-refresh')
  })
  afterEach(() => { api.defaults.adapter = originalAdapter; vi.restoreAllMocks() })

  it('shares a refresh between concurrent requests and stores rotated credentials', async () => {
    const refresh = vi.spyOn(axios, 'post').mockResolvedValue({ data: { access: 'new-access', refresh: 'new-refresh' } })
    api.defaults.adapter = async config => {
      if (config.headers.get('Authorization') === 'Bearer expired') {
        throw new AxiosError('unauthorized', 'ERR_BAD_REQUEST', config, undefined, { data: {}, status: 401, statusText: 'Unauthorized', headers: new AxiosHeaders(), config })
      }
      return { data: 'ok', status: 200, statusText: 'OK', headers: new AxiosHeaders(), config }
    }
    const responses = await Promise.all([api.patch('/products/a/', {}), api.get('/auth/profile/')])
    expect(responses.map(r => r.data)).toEqual(['ok', 'ok'])
    expect(refresh).toHaveBeenCalledTimes(1)
    expect(localStorage.getItem('access_token')).toBe('new-access')
    expect(localStorage.getItem('refresh_token')).toBe('new-refresh')
  })

  it('keeps credentials when refresh fails due to a network outage', async () => {
    vi.spyOn(axios, 'post').mockRejectedValue(new AxiosError('Network error', 'ERR_NETWORK'))
    api.defaults.adapter = async config => { throw new AxiosError('unauthorized', 'ERR_BAD_REQUEST', config, undefined, { data: {}, status: 401, statusText: 'Unauthorized', headers: new AxiosHeaders(), config }) }
    await expect(api.patch('/products/a/', {})).rejects.toThrow('Network error')
    expect(localStorage.getItem('refresh_token')).toBe('old-refresh')
    expect(sessionState.notice).toBe('unavailable')
  })

  it('clears invalid credentials and announces expiry only once for concurrent failures', async () => {
    const listener = vi.fn()
    window.addEventListener('bynzuri:session-expired', listener)
    vi.spyOn(axios, 'post').mockRejectedValue(new AxiosError('invalid refresh', 'ERR_BAD_REQUEST', undefined, undefined, { data: {}, status: 401, statusText: 'Unauthorized', headers: new AxiosHeaders(), config: {} as never }))
    api.defaults.adapter = async config => { throw new AxiosError('unauthorized', 'ERR_BAD_REQUEST', config, undefined, { data: {}, status: 401, statusText: 'Unauthorized', headers: new AxiosHeaders(), config }) }
    await Promise.allSettled([api.get('/auth/profile/'), api.get('/orders/')])
    expect(localStorage.getItem('refresh_token')).toBeNull()
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(sessionState.notice).toBe('expired')
    expect(listener).toHaveBeenCalledTimes(1)
    window.removeEventListener('bynzuri:session-expired', listener)
  })

  it('announces expiry if a freshly refreshed access token is also rejected', async () => {
    vi.spyOn(axios, 'post').mockResolvedValue({ data: { access: 'new-access', refresh: 'new-refresh' } })
    api.defaults.adapter = async config => { throw new AxiosError('unauthorized', 'ERR_BAD_REQUEST', config, undefined, { data: {}, status: 401, statusText: 'Unauthorized', headers: new AxiosHeaders(), config }) }
    await expect(api.get('/auth/profile/')).rejects.toThrow('unauthorized')
    expect(sessionState.notice).toBe('expired')
    expect(localStorage.getItem('refresh_token')).toBeNull()
  })
})
