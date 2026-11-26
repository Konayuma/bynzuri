import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { sessionExpired, sessionUnavailable } from './session'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/+$/, '')
declare const __PAGES_SESSION_PROXY__: boolean
const REQUEST_TIMEOUT = 30000
const SESSION_HINT = 'bynzuri_session'
let accessToken: string | null = null
let generation = 0
let refreshInFlight: Promise<string> | null = null

// Credentials from older versions are deliberately discarded on upgrade.
localStorage.removeItem('access_token')
localStorage.removeItem('refresh_token')

export const publicApi: AxiosInstance = axios.create({ baseURL: API_BASE_URL, timeout: REQUEST_TIMEOUT })
export const sessionApi: AxiosInstance = axios.create({ baseURL: __PAGES_SESSION_PROXY__ ? '/api' : API_BASE_URL, timeout: REQUEST_TIMEOUT, withCredentials: true })
const api: AxiosInstance = axios.create({ baseURL: API_BASE_URL, timeout: REQUEST_TIMEOUT, headers: { 'Content-Type': 'application/json' } })

export function getAccessToken() { return accessToken }
export function hasSession() { return !!accessToken || localStorage.getItem(SESSION_HINT) === '1' }
export function setAccessToken(token: string) { generation++; accessToken = token; localStorage.setItem(SESSION_HINT, '1') }
export function clearSession() { generation++; accessToken = null; localStorage.removeItem(SESSION_HINT) }
export function withSessionLock<T>(operation: () => Promise<T>): Promise<T> {
  return typeof navigator !== 'undefined' && navigator.locks
    ? navigator.locks.request('bynzuri-token-refresh', operation)
    : operation()
}

export async function csrfHeaders() {
  const response = await sessionApi.get('/auth/csrf/')
  if (typeof response.data?.csrfToken !== 'string') throw new Error('Invalid CSRF response')
  return { 'X-CSRFToken': response.data.csrfToken }
}

export async function refreshAccessToken(): Promise<string> {
  if (refreshInFlight) return refreshInFlight
  const currentGeneration = generation
  const performRefresh = async () => {
    const headers = await csrfHeaders()
    const response = await sessionApi.post('/auth/token/refresh/', {}, { headers })
    const access = response.data?.access
    if (typeof access !== 'string' || !access) throw new Error('Invalid refresh response')
    if (generation !== currentGeneration) throw new Error('Session changed')
    accessToken = access
    localStorage.setItem(SESSION_HINT, '1')
    return access
  }
  refreshInFlight = withSessionLock(performRefresh).finally(() => { refreshInFlight = null })
  return refreshInFlight
}

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (accessToken && config.headers) config.headers.Authorization = `Bearer ${accessToken}`
  return config
})

api.interceptors.response.use(response => response, async error => {
  const original = error.config
  if (!error.response && original?.headers?.Authorization) sessionUnavailable()
  if (error.response?.status !== 401 || !original || !hasSession()) return Promise.reject(error)
  if (original._retry) {
    if (accessToken && original.headers?.Authorization === `Bearer ${accessToken}`) { clearSession(); sessionExpired() }
    return Promise.reject(error)
  }
  original._retry = true
  // A concurrent request may already have refreshed the token after this
  // request was sent. Retry with it rather than rotating the cookie again.
  if (accessToken && original.headers?.Authorization && original.headers.Authorization !== `Bearer ${accessToken}`) {
    original.headers.Authorization = `Bearer ${accessToken}`
    return api(original)
  }
  const currentGeneration = generation
  try {
    const access = await refreshAccessToken()
    original.headers.Authorization = `Bearer ${access}`
    return api(original)
  } catch (cause) {
    if (generation === currentGeneration) {
      if (axios.isAxiosError(cause) && [400, 401].includes(cause.response?.status ?? 0)) { clearSession(); sessionExpired() }
      else sessionUnavailable()
    }
    return Promise.reject(cause)
  }
})

export default api
