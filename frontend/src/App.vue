<script setup lang="ts">
import { onMounted } from 'vue'
import AppNavbar from '@/layouts/AppNavbar.vue'
import AppFooter from '@/layouts/AppFooter.vue'
import CartDrawer from '@/components/cart/CartDrawer.vue'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'
import { useUIStore } from '@/stores/ui'

const userStore = useUserStore()
const cartStore = useCartStore()
const uiStore = useUIStore()

onMounted(async () => {
  cartStore.initGuestCart()
  if (localStorage.getItem('access_token')) {
    await userStore.fetchProfile()
    await cartStore.mergeGuestCart()
    await cartStore.fetchCart()
  }
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-background">
    <AppNavbar />
    <main class="flex-1">
      <router-view />
    </main>
    <AppFooter />
    <CartDrawer
      :open="uiStore.isCartOpen"
      @close="uiStore.closeCart"
    />
  </div>
</template>
