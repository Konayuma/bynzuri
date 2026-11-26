<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, onErrorCaptured, defineAsyncComponent, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppNavbar from '@/layouts/AppNavbar.vue'
import AppFooter from '@/layouts/AppFooter.vue'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'
import { useUIStore } from '@/stores/ui'
import { sessionState, sessionUnavailable } from '@/services/session'
import { hasSession } from '@/services/api'

const CartDrawer = defineAsyncComponent(() => import('@/components/cart/CartDrawer.vue'))

const userStore = useUserStore()
const cartStore = useCartStore()
const uiStore = useUIStore()
const router = useRouter()

const routeContainer = ref<HTMLElement | null>(null)
const isRouteAnimating = ref(false)
const retryingSession = ref(false)
const updateAvailable = ref(false)
const routeError = ref(false)
const navigating = ref(false)

onErrorCaptured(() => {
  routeError.value = true
  return false
})
let navigationTimer: ReturnType<typeof setTimeout> | undefined
let removeNavigationStart: (() => void) | undefined
let removeNavigationEnd: (() => void) | undefined
let removeNavigationError: (() => void) | undefined
function finishNavigation() {
  clearTimeout(navigationTimer)
  navigating.value = false
}
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
    if (!userStore.isAuthenticated && hasSession()) sessionUnavailable()
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
  removeNavigationStart = router.beforeEach(() => {
    clearTimeout(navigationTimer)
    navigationTimer = setTimeout(() => { navigating.value = true }, 200)
  })
  removeNavigationEnd = router.afterEach(finishNavigation)
  removeNavigationError = router.onError(finishNavigation)
  window.addEventListener('bynzuri:session-expired', resetDisplayedCart)
  window.addEventListener('vite:preloadError', handlePreloadError)
  cartStore.initGuestCart()
  if (hasSession()) {
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
  finishNavigation()
  removeNavigationStart?.()
  removeNavigationEnd?.()
  removeNavigationError?.()
  window.removeEventListener('bynzuri:session-expired', resetDisplayedCart)
  window.removeEventListener('vite:preloadError', handlePreloadError)
})

watch(() => router.currentRoute.value.path, (newPath, oldPath) => {
  routeError.value = false
  if (newPath === oldPath) return
  const el = routeContainer.value
  if (!el) return
  isRouteAnimating.value = false
  requestAnimationFrame(() => {
    isRouteAnimating.value = true
  })
})

function handleToastAction() {
  const action = uiStore.toast?.onAction
  uiStore.dismissToast()
  action?.()
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-background">
    <div class="flex min-h-screen min-h-[100dvh] flex-col">
    <div v-if="navigating" role="status" aria-live="polite" class="fixed top-3 left-1/2 z-[70] -translate-x-1/2 rounded-full border border-primary/50 bg-white px-4 py-2 text-sm font-medium text-dark shadow-lg">
      Loading page…
    </div>
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
        v-if="routeError"
        role="alert"
        class="mx-auto max-w-md px-4 py-20 text-center"
      >
        <h1 class="font-heading text-xl font-semibold text-dark">Something went wrong</h1>
        <p class="mt-2 text-sm text-muted">We couldn’t display this page right now. Try reloading to continue.</p>
        <div class="mt-5 flex items-center justify-center gap-3">
          <button type="button" class="min-h-11 rounded-full bg-dark px-5 text-sm font-medium text-background hover:bg-dark/90" @click="reloadApplication">Reload page</button>
          <router-link to="/" class="min-h-11 inline-flex items-center px-4 text-sm font-medium text-dark underline underline-offset-4" @click="routeError = false">Go home</router-link>
        </div>
      </div>
      <div
        v-else
        ref="routeContainer"
        class="route-transition"
        :class="{ 'route-enter': isRouteAnimating }"
      >
        <router-view />
      </div>
    </main>
    </div>
    <AppFooter v-if="!router.currentRoute.value.meta.standalone && !router.currentRoute.value.meta.adminArea" />
    <CartDrawer
      v-if="uiStore.isCartOpen && !router.currentRoute.value.meta.adminArea"
      :open="uiStore.isCartOpen"
      @close="uiStore.closeCart"
    />
    <Transition name="toast-slide">
      <div
        v-if="uiStore.toast"
        :key="uiStore.toast.id"
        role="status"
        aria-live="polite"
        class="fixed bottom-4 left-4 right-4 sm:left-auto sm:right-6 sm:bottom-6 z-[60] mx-auto sm:mx-0 max-w-sm rounded-2xl bg-dark text-background px-4 py-3 shadow-xl flex items-center justify-between gap-3"
      >
        <p class="text-sm leading-snug">{{ uiStore.toast.message }}</p>
        <div class="flex items-center gap-2 shrink-0">
          <button
            v-if="uiStore.toast.actionLabel"
            type="button"
            class="text-xs font-semibold uppercase tracking-wider text-primary underline underline-offset-4 hover:text-white min-h-9 px-1"
            @click="handleToastAction"
          >
            {{ uiStore.toast.actionLabel }}
          </button>
          <button
            type="button"
            class="text-background/70 hover:text-white p-1.5 rounded-lg"
            aria-label="Dismiss notification"
            @click="uiStore.dismissToast()"
          >
            ✕
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style>
.route-transition {
  opacity: 1;
  transform: translateY(0);
}
.route-enter {
  animation: routeFadeIn 0.2s ease-out;
}
@keyframes routeFadeIn {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.toast-slide-enter-from,
.toast-slide-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
