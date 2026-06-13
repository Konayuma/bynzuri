import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUIStore = defineStore('ui', () => {
  const isCartOpen = ref(false)
  const isMobileMenuOpen = ref(false)
  const isSearchOpen = ref(false)

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

  return {
    isCartOpen,
    isMobileMenuOpen,
    isSearchOpen,
    toggleCart,
    openCart,
    closeCart,
    toggleMobileMenu,
    closeMobileMenu
  }
})
