<script setup lang="ts">
import { ref, watch, onMounted, defineAsyncComponent } from 'vue'
import { useRouter } from 'vue-router'
import AppNavbar from '@/layouts/AppNavbar.vue'
import AppFooter from '@/layouts/AppFooter.vue'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'
import { useUIStore } from '@/stores/ui'

const CartDrawer = defineAsyncComponent(() => import('@/components/cart/CartDrawer.vue'))

const userStore = useUserStore()
const cartStore = useCartStore()
const uiStore = useUIStore()
const router = useRouter()

const routeContainer = ref<HTMLElement | null>(null)
const isRouteAnimating = ref(false)

onMounted(async () => {
  cartStore.initGuestCart()
  if (localStorage.getItem('access_token')) {
    const profilePromise = userStore.fetchProfile()
    await profilePromise
    if (userStore.isAuthenticated) {
      try {
        await cartStore.mergeGuestCart()
        await cartStore.fetchCart()
      } catch {
        cartStore.initGuestCart()
      }
    }
  }
})

watch(() => router.currentRoute.value, () => {
  const el = routeContainer.value
  if (!el) return
  isRouteAnimating.value = false
  requestAnimationFrame(() => {
    isRouteAnimating.value = true
  })
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-background">
    <AppNavbar />
    <main class="flex-1">
      <div
        ref="routeContainer"
        class="route-transition"
        :class="{ 'route-enter': isRouteAnimating }"
      >
        <router-view />
      </div>
    </main>
    <AppFooter v-if="!router.currentRoute.value.meta.standalone" />
    <CartDrawer
      v-if="uiStore.isCartOpen"
      :open="uiStore.isCartOpen"
      @close="uiStore.closeCart"
    />
  </div>
</template>

<style>
.route-transition {
  opacity: 1;
  transform: translateY(0);
}
.route-enter {
  animation: routeFadeIn 0.4s ease-out;
}
@keyframes routeFadeIn {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
