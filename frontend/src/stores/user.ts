import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { authService } from '@/services/auth.service'
import { sessionExpired, sessionRestored, sessionUnavailable } from '@/services/session'
import axios from 'axios'
import { clearSession, getAccessToken, hasSession, refreshAccessToken, setAccessToken } from '@/services/api'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.is_staff === true)

  async function fetchProfile() {
    if (!hasSession()) return

    loading.value = true
    try {
      if (!getAccessToken()) await refreshAccessToken()
      user.value = await authService.getProfile()
      sessionRestored()
    } catch (error) {
      if (axios.isAxiosError(error) && [400, 401].includes(error.response?.status ?? 0)) { clearSession(); user.value = null; sessionExpired() }
      else if (!hasSession()) user.value = null
      else if (!axios.isAxiosError(error) || !error.response || error.response.status >= 500) sessionUnavailable()
      throw error
    } finally {
      loading.value = false
    }
  }

  async function login(email: string, password: string) {
    const tokens = await authService.login(email, password)
    setAccessToken(tokens.access)
    await fetchProfile()
  }

  async function register(data: {
    email: string
    password: string
    first_name: string
    last_name: string
    phone: string
  }) {
    await authService.register(data)
  }

  async function updateProfile(data: Partial<User>) {
    loading.value = true
    try {
      user.value = await authService.updateProfile(data)
    } finally {
      loading.value = false
    }
  }

  function logout() {
    user.value = null
    clearSession()
    void authService.logout().catch(() => sessionUnavailable())
    sessionRestored()
  }

  if (typeof window !== 'undefined') {
    window.addEventListener('bynzuri:session-expired', () => { user.value = null })
    window.addEventListener('storage', event => {
      if (event.key === 'bynzuri_session' && event.oldValue && !event.newValue) {
        clearSession()
        user.value = null
        sessionExpired()
      }
    })
  }

  return {
    user,
    loading,
    isAuthenticated,
    isAdmin,
    fetchProfile,
    login,
    register,
    updateProfile,
    logout
  }
})
