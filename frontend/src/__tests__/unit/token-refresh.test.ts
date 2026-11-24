import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { AxiosError, AxiosHeaders } from 'axios'
import type { InternalAxiosRequestConfig } from 'axios'
import api, { sessionApi, setAccessToken, getAccessToken, clearSession } from '@/services/api'
import { sessionState } from '@/services/session'

const originalAdapter = api.defaults.adapter
const unauthorized = (config: InternalAxiosRequestConfig) => new AxiosError('unauthorized', 'ERR_BAD_REQUEST', config, undefined, { data: {}, status: 401, statusText: 'Unauthorized', headers: new AxiosHeaders(), config })

describe('expired access tokens', () => {
  beforeEach(() => {
    localStorage.clear(); clearSession(); sessionState.notice = null; setAccessToken('expired')
    vi.spyOn(sessionApi, 'get').mockResolvedValue({ data: { csrfToken: 'csrf' } })
  })
  afterEach(() => { api.defaults.adapter = originalAdapter; clearSession(); vi.restoreAllMocks() })

  it('shares a cookie refresh between concurrent requests without storing tokens', async () => {
    const refresh = vi.spyOn(sessionApi, 'post').mockResolvedValue({ data: { access: 'new-access' } })
    api.defaults.adapter = async config => {
      if (config.headers.get('Authorization') === 'Bearer expired') throw unauthorized(config)
      return { data: 'ok', status: 200, statusText: 'OK', headers: new AxiosHeaders(), config }
    }
    const responses = await Promise.all([api.patch('/products/a/', {}), api.get('/auth/profile/')])
    expect(responses.map(r => r.data)).toEqual(['ok', 'ok'])
    expect(refresh).toHaveBeenCalledTimes(1)
    expect(refresh).toHaveBeenCalledWith('/auth/token/refresh/', {}, { headers: { 'X-CSRFToken': 'csrf' } })
    expect(getAccessToken()).toBe('new-access')
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
  })
  it('retains session when refresh has a network outage', async () => {
    vi.spyOn(sessionApi, 'post').mockRejectedValue(new AxiosError('Network error', 'ERR_NETWORK'))
    api.defaults.adapter = async config => { throw unauthorized(config) }
    await expect(api.get('/auth/profile/')).rejects.toThrow('Network error')
    expect(getAccessToken()).toBe('expired')
    expect(sessionState.notice).toBe('unavailable')
  })
  it('clears a rejected refresh and announces expiry once', async () => {
    const listener = vi.fn(); window.addEventListener('bynzuri:session-expired', listener)
    vi.spyOn(sessionApi, 'post').mockRejectedValue(unauthorized({} as never))
    api.defaults.adapter = async config => { throw unauthorized(config) }
    await Promise.allSettled([api.get('/auth/profile/'), api.get('/orders/')])
    expect(getAccessToken()).toBeNull()
    expect(sessionState.notice).toBe('expired')
    expect(listener).toHaveBeenCalledTimes(1)
    window.removeEventListener('bynzuri:session-expired', listener)
  })
  it('announces expiry if the refreshed access token is rejected', async () => {
    vi.spyOn(sessionApi, 'post').mockResolvedValue({ data: { access: 'new-access' } })
    api.defaults.adapter = async config => { throw unauthorized(config) }
    await expect(api.get('/auth/profile/')).rejects.toThrow('unauthorized')
    expect(sessionState.notice).toBe('expired')
    expect(getAccessToken()).toBeNull()
  })
})
