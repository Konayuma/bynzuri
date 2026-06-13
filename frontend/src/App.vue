<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { gsap } from 'gsap'
import AppNavbar from '@/layouts/AppNavbar.vue'
import AppFooter from '@/layouts/AppFooter.vue'
import CartDrawer from '@/components/cart/CartDrawer.vue'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'
import { useUIStore } from '@/stores/ui'

const userStore = useUserStore()
const cartStore = useCartStore()
const uiStore = useUIStore()
const router = useRouter()

const routeContainer = ref<HTMLElement | null>(null)

onMounted(async () => {
  cartStore.initGuestCart()
  if (localStorage.getItem('access_token')) {
    await userStore.fetchProfile()
    await cartStore.mergeGuestCart()
    await cartStore.fetchCart()
  }
})

watch(() => router.currentRoute.value, () => {
  const el = routeContainer.value
  if (!el) return
  gsap.fromTo(el, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' })
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-background">
    <AppNavbar />
    <main class="flex-1">
      <div ref="routeContainer" class="contents">
        <router-view />
      </div>
    </main>
    <AppFooter />
    <CartDrawer
      :open="uiStore.isCartOpen"
      @close="uiStore.closeCart"
    />
  </div>
</template>
