import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/+$/, '')
const REQUEST_TIMEOUT = 30000

// Public storefront reads must not inherit an expired or unrelated login token.
export const publicApi: AxiosInstance = axios.create({ baseURL: API_BASE_URL, timeout: REQUEST_TIMEOUT })

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token')
  if (token && config.headers) config.headers.Authorization = `Bearer ${token}`
  return config
})

// One refresh for simultaneous expired requests prevents rotating the same token twice.
let refreshInFlight: Promise<string> | null = null
async function refreshAccessToken(): Promise<string> {
  if (refreshInFlight) return refreshInFlight
  const refresh = localStorage.getItem('refresh_token')
  if (!refresh) throw new Error('No refresh token')
  refreshInFlight = (async () => {
    const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, { refresh }, { timeout: REQUEST_TIMEOUT })
    const access = response.data?.access
    if (typeof access !== 'string' || !access) throw new Error('Invalid refresh response')
    // Do not overwrite credentials if the user signed out or signed in again meanwhile.
    if (localStorage.getItem('refresh_token') !== refresh) throw new Error('Session changed')
    localStorage.setItem('access_token', access)
    if (typeof response.data.refresh === 'string' && response.data.refresh) {
      localStorage.setItem('refresh_token', response.data.refresh)
    }
    return access
  })().finally(() => { refreshInFlight = null })
  return refreshInFlight
}

api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config
    if (error.response?.status !== 401 || !originalRequest || originalRequest._retry) return Promise.reject(error)
    originalRequest._retry = true
    const oldRefresh = localStorage.getItem('refresh_token')
    try {
      const access = await refreshAccessToken()
      originalRequest.headers.Authorization = `Bearer ${access}`
      return api(originalRequest)
    } catch (refreshError) {
      // A timeout or network failure does not prove the session is invalid.
      if ((!oldRefresh || (axios.isAxiosError(refreshError) && [400, 401, 403].includes(refreshError.response?.status ?? 0))) && localStorage.getItem('refresh_token') === oldRefresh) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      }
      return Promise.reject(refreshError)
    }
  }
)

export default api
