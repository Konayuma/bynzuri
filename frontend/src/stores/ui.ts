import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface UIToast {
  id: number
  message: string
  actionLabel?: string
  onAction?: () => void
}

export const useUIStore = defineStore('ui', () => {
  const isCartOpen = ref(false)
  const isMobileMenuOpen = ref(false)
  const isSearchOpen = ref(false)
  const toast = ref<UIToast | null>(null)
  let toastTimer: ReturnType<typeof setTimeout> | undefined
  let toastId = 0

  function toggleCart() {
    isCartOpen.value = !isCartOpen.value
  }

  function openCart() {
    isCartOpen.value = true
  }

  function closeCart() {
    isCartOpen.value = false
  }

  function toggleMobileMenu() {
    isMobileMenuOpen.value = !isMobileMenuOpen.value
  }

  function closeMobileMenu() {
    isMobileMenuOpen.value = false
  }

  function showToast(message: string, options?: { actionLabel?: string; onAction?: () => void; duration?: number }) {
    if (toastTimer) clearTimeout(toastTimer)
    toast.value = {
      id: ++toastId,
      message,
      actionLabel: options?.actionLabel,
      onAction: options?.onAction,
    }
    toastTimer = setTimeout(() => {
      toast.value = null
    }, options?.duration ?? 3500)
  }

  function dismissToast() {
    if (toastTimer) clearTimeout(toastTimer)
    toast.value = null
  }

  return {
    isCartOpen,
    isMobileMenuOpen,
    isSearchOpen,
    toast,
    toggleCart,
    openCart,
    closeCart,
    toggleMobileMenu,
    closeMobileMenu,
    showToast,
    dismissToast
  }
})
