<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ShoppingBag, User, Search, Menu, X, Heart } from '@lucide/vue'
import { useCartStore } from '@/stores/cart'
import { useUserStore } from '@/stores/user'
import { useUIStore } from '@/stores/ui'

const router = useRouter()
const route = useRoute()
const cartStore = useCartStore()
const userStore = useUserStore()
const uiStore = useUIStore()

const searchQuery = ref('')
const searchInputRef = ref<HTMLInputElement | null>(null)
const mobileSearchOpen = ref(false)
const scrolled = ref(false)
const hidden = ref(false)
let lastScroll = 0

function handleSearch() {
  const q = searchQuery.value.trim()
  if (q) {
    router.push({ name: 'catalog', query: { search: q } })
  } else if (route.name === 'catalog') {
    router.push({ name: 'catalog' })
  }
}

function clearSearch() {
  searchQuery.value = ''
  if (route.name === 'catalog') {
    router.push({ name: 'catalog' })
  }
}

function onScroll() {
  const y = window.scrollY
  scrolled.value = y > 20
  hidden.value = y > lastScroll && y > 200
  lastScroll = y
}

watch(() => route.query.search, (val) => {
  searchQuery.value = (val as string) || ''
}, { immediate: true })

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
})
onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
})
</script>

<template>
  <header
    :class="[
      'sticky top-0 z-50 bg-background/95 backdrop-blur-lg border-b border-primary/20 transition-all duration-300',
      scrolled ? 'shadow-[0_1px_12px_rgba(0,0,0,0.04)]' : '',
      hidden ? '-translate-y-full' : 'translate-y-0'
    ]"
  >
    <!-- Main nav row -->
    <div class="max-w-7xl mx-auto px-4 h-[72px] flex items-center gap-4">
      <!-- Mobile menu toggle -->
      <button
        class="lg:hidden p-2 -ml-2 hover:bg-primary/30 rounded-lg transition-colors active:scale-95 shrink-0"
        @click="uiStore.toggleMobileMenu"
        aria-label="Toggle menu"
      >
        <Menu v-if="!uiStore.isMobileMenuOpen" class="w-6 h-6 text-dark" />
        <X v-else class="w-6 h-6 text-dark" />
      </button>

      <!-- Logo -->
      <router-link to="/" class="font-heading text-2xl font-bold text-dark tracking-tight hover:opacity-80 transition-opacity shrink-0">
        bynzuri
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
        <div class="relative w-full group">
          <Search class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted group-focus-within:text-dark transition-colors" />
          <input
            ref="searchInputRef"
            v-model="searchQuery"
            type="text"
            placeholder="Search products..."
            class="w-full pl-10 pr-9 py-2.5 bg-primary/20 border border-transparent rounded-full text-sm text-dark placeholder:text-muted/60 focus:outline-none focus:bg-white focus:border-primary/40 transition-all duration-200"
            @keyup.enter="handleSearch"
          />
          <button
            v-if="searchQuery"
            class="absolute right-3 top-1/2 -translate-y-1/2 p-0.5 hover:bg-primary/30 rounded-full transition-colors"
            @click="clearSearch"
          >
            <X class="w-3.5 h-3.5 text-muted" />
          </button>
        </div>
      </div>

      <!-- Right icons -->
      <div class="flex items-center gap-1.5 shrink-0">
        <!-- Mobile search toggle -->
        <button
          class="lg:hidden p-2 hover:bg-primary/30 rounded-lg transition-colors active:scale-95"
          @click="mobileSearchOpen = !mobileSearchOpen"
          aria-label="Search"
        >
          <Search class="w-5 h-5 text-dark" />
        </button>

        <router-link
          to="/wishlist"
          class="p-2 hover:bg-primary/30 rounded-lg transition-colors active:scale-95"
          aria-label="Wishlist"
        >
          <Heart class="w-5 h-5 text-dark" />
        </router-link>

        <router-link
          :to="userStore.isAuthenticated ? '/account' : '/auth/login'"
          class="p-2 hover:bg-primary/30 rounded-lg transition-colors active:scale-95"
          aria-label="Account"
        >
          <User class="w-5 h-5 text-dark" />
        </router-link>

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
      class="lg:hidden overflow-hidden transition-all duration-300"
      :class="mobileSearchOpen ? 'max-h-20 opacity-100' : 'max-h-0 opacity-0'"
    >
      <div class="px-4 pb-3">
        <div class="relative">
          <Search class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search products..."
            class="w-full pl-10 pr-9 py-2.5 bg-primary/20 border border-transparent rounded-full text-sm text-dark placeholder:text-muted/60 focus:outline-none focus:bg-white focus:border-primary/40 transition-all duration-200"
            @keyup.enter="handleSearch"
          />
          <button
            v-if="searchQuery"
            class="absolute right-3 top-1/2 -translate-y-1/2 p-0.5 hover:bg-primary/30 rounded-full transition-colors"
            @click="clearSearch"
          >
            <X class="w-3.5 h-3.5 text-muted" />
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile menu -->
    <div
      v-if="uiStore.isMobileMenuOpen"
      class="lg:hidden border-t border-primary/20 bg-background"
    >
      <nav class="px-4 py-4 space-y-3">
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
