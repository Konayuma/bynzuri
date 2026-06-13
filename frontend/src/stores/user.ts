import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { authService } from '@/services/auth.service'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function fetchProfile() {
    const token = localStorage.getItem('access_token')
    if (!token) return

    loading.value = true
    try {
      user.value = await authService.getProfile()
    } catch {
      user.value = null
    } finally {
      loading.value = false
    }
  }

  async function login(email: string, password: string) {
    const tokens = await authService.login(email, password)
    localStorage.setItem('access_token', tokens.access)
    localStorage.setItem('refresh_token', tokens.refresh)
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
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
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
