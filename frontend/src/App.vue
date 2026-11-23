<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, defineAsyncComponent, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppNavbar from '@/layouts/AppNavbar.vue'
import AppFooter from '@/layouts/AppFooter.vue'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'
import { useUIStore } from '@/stores/ui'
import { sessionState, sessionUnavailable } from '@/services/session'

const CartDrawer = defineAsyncComponent(() => import('@/components/cart/CartDrawer.vue'))

const userStore = useUserStore()
const cartStore = useCartStore()
const uiStore = useUIStore()
const router = useRouter()

const routeContainer = ref<HTMLElement | null>(null)
const isRouteAnimating = ref(false)
const retryingSession = ref(false)
const updateAvailable = ref(false)
const signInDestination = computed(() => {
  const route = router.currentRoute.value
  const original = route.name === 'session-unavailable' ? route.query.redirect : route.fullPath
  return typeof original === 'string' && original.startsWith('/') && !original.startsWith('//') ? original : '/'
})

function resetDisplayedCart() {
  cartStore.cart = null
  cartStore.initGuestCart()
}

function handlePreloadError(event: Event) {
  event.preventDefault()
  updateAvailable.value = true
}

function reloadApplication() {
  window.location.reload()
}

async function retrySession() {
  retryingSession.value = true
  try {
    await userStore.fetchProfile()
    if (!userStore.isAuthenticated && localStorage.getItem('access_token')) sessionUnavailable()
    if (userStore.isAuthenticated && router.currentRoute.value.name === 'session-unavailable') {
      const target = router.currentRoute.value.query.redirect
      await router.replace(typeof target === 'string' && target.startsWith('/') && !target.startsWith('//') ? target : '/')
    }
  } catch {
    // The session notice explains whether to retry or sign in again.
  } finally {
    retryingSession.value = false
  }
}

onMounted(async () => {
  window.addEventListener('bynzuri:session-expired', resetDisplayedCart)
  window.addEventListener('vite:preloadError', handlePreloadError)
  cartStore.initGuestCart()
  if (localStorage.getItem('access_token')) {
    const profilePromise = userStore.fetchProfile()
    try { await profilePromise } catch { return }
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
onUnmounted(() => {
  window.removeEventListener('bynzuri:session-expired', resetDisplayedCart)
  window.removeEventListener('vite:preloadError', handlePreloadError)
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
    <AppNavbar v-if="!router.currentRoute.value.meta.adminArea" />
    <div v-if="updateAvailable" role="alert" class="border-b border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-950">
      <div class="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3">
        <p>This page couldn’t load. A site update or connection issue may be the cause. Reload when you’re ready; unsaved changes on this page may be lost.</p>
        <button type="button" class="font-semibold underline" @click="reloadApplication">Reload page</button>
      </div>
    </div>
    <div v-if="sessionState.notice" role="alert" class="border-b border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-950">
      <div class="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3">
        <p v-if="sessionState.notice === 'expired'">Your session has expired. Sign in again to continue. Your current page remains open until you choose to leave.</p>
        <p v-else>We can’t check your session right now. Check your connection and try again; your session has not been cleared.</p>
        <router-link v-if="sessionState.notice === 'expired'" :to="{ name: 'login', query: { reason: 'expired', redirect: signInDestination } }" class="font-semibold underline">Sign in again</router-link>
        <button v-else type="button" class="font-semibold underline disabled:opacity-50" :disabled="retryingSession" @click="retrySession">{{ retryingSession ? 'Checking…' : 'Try again' }}</button>
      </div>
    </div>
    <main class="flex-1">
      <div
        ref="routeContainer"
        class="route-transition"
        :class="{ 'route-enter': isRouteAnimating }"
      >
        <router-view />
      </div>
    </main>
    <AppFooter v-if="!router.currentRoute.value.meta.standalone && !router.currentRoute.value.meta.adminArea" />
    <CartDrawer
      v-if="uiStore.isCartOpen && !router.currentRoute.value.meta.adminArea"
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
