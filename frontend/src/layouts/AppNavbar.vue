<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ShoppingBag, User, Search, Menu, X, Heart, Package, MapPin, LogOut, LogIn, UserPlus, LayoutDashboard } from '@lucide/vue'
import { useCartStore } from '@/stores/cart'
import { useUserStore } from '@/stores/user'
import { useUIStore } from '@/stores/ui'
import ProductSearch from '@/components/search/ProductSearch.vue'

const router = useRouter()
const route = useRoute()
const cartStore = useCartStore()
const userStore = useUserStore()
const uiStore = useUIStore()

const searchQuery = ref('')
const mobileSearchOpen = ref(false)
const scrolled = ref(false)
const accountOpen = ref(false)
const accountMenu = ref<HTMLElement | null>(null)
const accountTrigger = ref<HTMLButtonElement | null>(null)

function closeAccount(restoreFocus = false) {
  accountOpen.value = false
  if (restoreFocus) nextTick(() => accountTrigger.value?.focus())
}

function onOutsidePointer(event: PointerEvent) {
  if (accountOpen.value && !accountMenu.value?.contains(event.target as Node)) closeAccount()
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && accountOpen.value) {
    event.preventDefault()
    closeAccount(true)
  }
}

function signOut() {
  userStore.logout()
  cartStore.cart = null
  cartStore.initGuestCart()
  closeAccount()
  router.push('/')
}

function handleSearch() {
  const q = searchQuery.value.trim()
  if (q) {
    router.push({ name: 'catalog', query: { search: q } })
    mobileSearchOpen.value = false
    uiStore.closeMobileMenu()
  } else if (route.name === 'catalog') {
    router.push({ name: 'catalog' })
  }
}

async function toggleSearch() {
  mobileSearchOpen.value = !mobileSearchOpen.value
  if (mobileSearchOpen.value) { await nextTick(); document.getElementById('mobile-product-search')?.focus() }
}

function onScroll() {
  const y = window.scrollY
  scrolled.value = y > 20
}

watch(() => route.query.search, (val) => {
  searchQuery.value = (val as string) || ''
}, { immediate: true })

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
  document.addEventListener('pointerdown', onOutsidePointer)
  document.addEventListener('keydown', onKeydown)
})
onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  document.removeEventListener('pointerdown', onOutsidePointer)
  document.removeEventListener('keydown', onKeydown)
})
watch(() => route.fullPath, () => { mobileSearchOpen.value = false; uiStore.closeMobileMenu(); closeAccount() })
</script>

<template>
  <header
    :class="[
      'sticky top-0 z-50 bg-background/95 backdrop-blur-lg border-b border-primary/20 transition-all duration-300',
      scrolled ? 'shadow-[0_1px_12px_rgba(0,0,0,0.04)]' : '',
    ]"
  >
    <!-- Main nav row -->
    <div class="max-w-7xl mx-auto px-4 h-[72px] flex items-center gap-4">
      <!-- Mobile menu toggle -->
      <button
        class="lg:hidden p-2 -ml-2 hover:bg-primary/30 rounded-lg transition-colors active:scale-95 shrink-0"
        @click="uiStore.toggleMobileMenu"
        aria-label="Toggle menu"
        :aria-expanded="uiStore.isMobileMenuOpen"
      >
        <Menu v-if="!uiStore.isMobileMenuOpen" class="w-6 h-6 text-dark" />
        <X v-else class="w-6 h-6 text-dark" />
      </button>

      <!-- Logo -->
      <router-link to="/" class="brand-mark shrink-0 hover:opacity-80 transition-opacity">
        <span>HAIR &amp; SKINCARE</span><em>by Nzuri</em>
      </router-link>

      <!-- Desktop nav links -->
      <nav class="hidden lg:flex items-center gap-8 shrink-0">
        <router-link to="/catalog" class="text-sm font-medium text-muted hover:text-dark transition-colors relative after:absolute after:bottom-[-22px] after:left-0 after:w-full after:h-[2px] after:bg-dark after:scale-x-0 hover:after:scale-x-100 after:transition-transform after:duration-200">
          Shop All
        </router-link>
        <router-link to="/catalog?category=hair-care" class="text-sm font-medium text-muted hover:text-dark transition-colors relative after:absolute after:bottom-[-22px] after:left-0 after:w-full after:h-[2px] after:bg-dark after:scale-x-0 hover:after:scale-x-100 after:transition-transform after:duration-200">
          Hair Care
        </router-link>
        <router-link to="/catalog?category=hair-growth" class="text-sm font-medium text-muted hover:text-dark transition-colors relative after:absolute after:bottom-[-22px] after:left-0 after:w-full after:h-[2px] after:bg-dark after:scale-x-0 hover:after:scale-x-100 after:transition-transform after:duration-200">
          Hair Growth
        </router-link>
        <router-link to="/catalog?category=oils" class="text-sm font-medium text-muted hover:text-dark transition-colors relative after:absolute after:bottom-[-22px] after:left-0 after:w-full after:h-[2px] after:bg-dark after:scale-x-0 hover:after:scale-x-100 after:transition-transform after:duration-200">
          Oils
        </router-link>
      </nav>

      <!-- Desktop persistent search bar -->
      <div class="hidden lg:flex flex-1 max-w-md ml-auto mr-4">
        <ProductSearch v-model="searchQuery" @submit="handleSearch" />
      </div>

      <!-- Right icons -->
      <div class="flex items-center gap-1.5 shrink-0">
        <!-- Mobile search toggle -->
        <button
          class="lg:hidden p-2 hover:bg-primary/30 rounded-lg transition-colors active:scale-95"
          @click="toggleSearch"
          :aria-expanded="mobileSearchOpen"
          aria-controls="mobile-search"
          aria-label="Search"
        >
          <Search class="w-5 h-5 text-dark" />
        </button>

        <router-link
          to="/wishlist"
          class="hidden sm:block p-2 hover:bg-primary/30 rounded-lg transition-colors active:scale-95"
          aria-label="Wishlist"
        >
          <Heart class="w-5 h-5 text-dark" />
        </router-link>

        <div ref="accountMenu" class="account-wrap">
          <button ref="accountTrigger" type="button" class="account-trigger" aria-label="Account" aria-controls="account-popover" :aria-expanded="accountOpen" @click="accountOpen = !accountOpen">
            <User class="w-5 h-5" />
          </button>
          <Transition name="account-popover">
            <div v-if="accountOpen" id="account-popover" class="account-panel" aria-label="Account options" @focusout="(event) => { if (event.relatedTarget && !accountMenu?.contains(event.relatedTarget as Node)) closeAccount() }">
              <template v-if="userStore.isAuthenticated">
                <div class="account-identity">
                  <span class="account-avatar"><User class="w-5 h-5" /></span>
                  <div class="account-identity-text"><strong>{{ [userStore.user?.first_name, userStore.user?.last_name].filter(Boolean).join(' ') || 'My account' }}</strong><span>{{ userStore.user?.email }}</span></div>
                </div>
                <div class="account-links">
                  <router-link to="/account" @click="closeAccount()"><User /> <span>My profile</span></router-link>
                  <router-link to="/account/orders" @click="closeAccount()"><Package /> <span>Order history</span></router-link>
                  <router-link to="/account#saved-addresses" @click="closeAccount()"><MapPin /> <span>Saved addresses</span></router-link>
                  <router-link to="/wishlist" @click="closeAccount()"><Heart /> <span>Wishlist</span></router-link>
                  <router-link v-if="userStore.isAdmin" to="/admin" @click="closeAccount()"><LayoutDashboard /> <span>Admin dashboard</span></router-link>
                </div>
                <div class="account-signout"><button type="button" @click="signOut"><LogOut /> <span>Sign out</span></button></div>
              </template>
              <template v-else>
                <div class="account-welcome"><strong>Welcome to By Nzuri</strong><span>Sign in to view your orders and saved details.</span></div>
                <div class="account-links"><router-link to="/auth/login" @click="closeAccount()"><LogIn /> <span>Sign in</span></router-link><router-link to="/auth/register" @click="closeAccount()"><UserPlus /> <span>Create account</span></router-link><router-link to="/wishlist" @click="closeAccount()"><Heart /> <span>Wishlist</span></router-link></div>
              </template>
            </div>
          </Transition>
        </div>

        <button
          class="p-2 hover:bg-primary/30 rounded-lg transition-colors relative active:scale-95"
          @click="uiStore.openCart"
          aria-label="Open cart"
        >
          <ShoppingBag class="w-5 h-5 text-dark" />
          <span
            v-if="cartStore.itemCount > 0"
            class="absolute -top-0.5 -right-0.5 bg-dark text-white text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center"
          >
            {{ cartStore.itemCount }}
          </span>
        </button>
      </div>
    </div>

    <!-- Mobile search bar (slide down) -->
    <div
      v-if="mobileSearchOpen"
      id="mobile-search"
      class="lg:hidden"
    >
      <div class="px-4 pb-3">
        <ProductSearch v-model="searchQuery" mobile @submit="handleSearch" />
      </div>
    </div>

    <!-- Mobile menu -->
    <div
      v-if="uiStore.isMobileMenuOpen"
      class="lg:hidden border-t border-primary/20 bg-background"
    >
      <nav class="px-4 py-4 space-y-3">
        <router-link to="/wishlist" class="block py-2 text-sm font-medium text-muted hover:text-dark" @click="uiStore.closeMobileMenu">Wishlist</router-link>
        <router-link
          to="/catalog"
          class="block py-2 text-sm font-medium text-muted hover:text-dark transition-colors"
          @click="uiStore.closeMobileMenu"
        >
          Shop All
        </router-link>
        <router-link
          to="/catalog?category=hair-care"
          class="block py-2 text-sm font-medium text-muted hover:text-dark transition-colors"
          @click="uiStore.closeMobileMenu"
        >
          Hair Care
        </router-link>
        <router-link
          to="/catalog?category=hair-growth"
          class="block py-2 text-sm font-medium text-muted hover:text-dark transition-colors"
          @click="uiStore.closeMobileMenu"
        >
          Hair Growth
        </router-link>
        <router-link
          to="/catalog?category=oils"
          class="block py-2 text-sm font-medium text-muted hover:text-dark transition-colors"
          @click="uiStore.closeMobileMenu"
        >
          Oils
        </router-link>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.brand-mark { display:flex; flex-direction:column; color:#201a1a; line-height:1; }
.brand-mark span { font:700 10px Cinzel,serif; letter-spacing:.16em; white-space:nowrap; }
.brand-mark em { font:400 23px 'Great Vibes',cursive; margin-top:2px; }
.account-wrap { position: relative; }
.account-trigger { display:grid; place-items:center; width:44px; height:44px; border-radius:12px; color:#261f20; transition:background .15s, transform .15s; }
.account-trigger:hover, .account-trigger[aria-expanded="true"] { background:#f1e4e5; }
.account-trigger:active { transform:scale(.95); }
.account-trigger:focus-visible, .account-panel a:focus-visible, .account-panel button:focus-visible { outline:2px solid #875e64; outline-offset:2px; }
.account-panel { position:absolute; top:calc(100% + 10px); right:-48px; width:min(290px, calc(100vw - 24px)); max-height:calc(100dvh - 90px); overflow:auto; padding:8px; border:1px solid rgba(112,76,80,.14); border-radius:20px; background:rgba(255,252,251,.97); box-shadow:0 18px 50px rgba(45,27,30,.16), 0 3px 10px rgba(45,27,30,.06); transform-origin:calc(100% - 68px) top; z-index:10; }
.account-identity { display:flex; align-items:center; gap:12px; padding:12px 10px 16px; border-bottom:1px solid #eee4e4; }
.account-avatar { display:grid; place-items:center; width:42px; height:42px; flex:none; border-radius:50%; background:#f2e2e4; color:#513b3e; }
.account-identity-text { min-width:0; }
.account-identity-text strong, .account-identity-text span, .account-welcome strong, .account-welcome span { display:block; overflow-wrap:anywhere; }
.account-identity-text strong, .account-welcome strong { color:#2b2223; font-size:.9rem; font-weight:600; }
.account-identity-text span, .account-welcome span { color:#766a6b; font-size:.75rem; line-height:1.45; margin-top:3px; }
.account-welcome { padding:12px 10px 14px; border-bottom:1px solid #eee4e4; }
.account-links { padding:6px 0; }
.account-links a, .account-signout button { display:flex; align-items:center; gap:12px; width:100%; min-height:42px; padding:9px 10px; border-radius:11px; color:#342a2b; text-align:left; font-size:.875rem; transition:background .15s; }
.account-links a:hover, .account-signout button:hover { background:#f7edee; }
.account-links svg, .account-signout svg { width:17px; height:17px; flex:none; color:#857477; }
.account-signout { border-top:1px solid #eee4e4; padding-top:6px; }
.account-signout button, .account-signout svg { color:#a3434d; }
.account-popover-enter-active, .account-popover-leave-active { transition:opacity .16s ease, transform .16s ease; }
.account-popover-enter-from, .account-popover-leave-to { opacity:0; transform:translateY(-4px) scale(.98); }
@media (prefers-reduced-motion:reduce) { .account-popover-enter-active, .account-popover-leave-active, .account-trigger { transition:none; } }
@media (prefers-contrast:more) { .account-panel { background:#fff; border:2px solid #513b3e; } }
</style>
