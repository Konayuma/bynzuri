import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// Public storefront reads must not inherit an expired or unrelated login token.
export const publicApi: AxiosInstance = axios.create({ baseURL: API_BASE_URL })

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) {
          throw new Error('No refresh token')
        }

        const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken
        })

        const { access } = response.data
        localStorage.setItem('access_token', access)

        originalRequest.headers.Authorization = `Bearer ${access}`
        return api(originalRequest)
      } catch {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        const path = window.location.pathname
        if (path === '/checkout' || path.startsWith('/account') || path.startsWith('/admin') || path.startsWith('/order/')) {
          window.location.href = `/auth/login?redirect=${encodeURIComponent(path + window.location.search)}`
        }
        return Promise.reject(error)
      }
    }

    return Promise.reject(error)
  }
)

export default api
