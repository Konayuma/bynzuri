<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ShoppingBag, User, Search, Menu, X } from '@lucide/vue'
import { useCartStore } from '@/stores/cart'
import { useUserStore } from '@/stores/user'
import { useUIStore } from '@/stores/ui'

const router = useRouter()
const cartStore = useCartStore()
const userStore = useUserStore()
const uiStore = useUIStore()

const searchQuery = ref('')
const isSearchVisible = ref(false)

function handleSearch() {
  if (searchQuery.value.trim()) {
    router.push({ name: 'catalog', query: { search: searchQuery.value.trim() } })
    searchQuery.value = ''
    isSearchVisible.value = false
  }
}
</script>

<template>
  <header class="sticky top-0 z-50 bg-background/95 backdrop-blur-lg border-b border-primary/20">
    <div class="max-w-7xl mx-auto px-4 h-[72px] flex items-center justify-between">
      <button
        class="lg:hidden p-2 -ml-2"
        @click="uiStore.toggleMobileMenu"
        aria-label="Toggle menu"
      >
        <Menu v-if="!uiStore.isMobileMenuOpen" class="w-6 h-6 text-dark" />
        <X v-else class="w-6 h-6 text-dark" />
      </button>

      <router-link to="/" class="font-heading text-2xl font-bold text-dark tracking-tight">
        bynzuri
      </router-link>

      <nav class="hidden lg:flex items-center gap-8">
        <router-link to="/catalog" class="text-sm font-medium text-muted hover:text-dark transition-colors">
          Shop All
        </router-link>
        <router-link to="/catalog?category=hair-care" class="text-sm font-medium text-muted hover:text-dark transition-colors">
          Hair Care
        </router-link>
        <router-link to="/catalog?category=hair-growth" class="text-sm font-medium text-muted hover:text-dark transition-colors">
          Hair Growth
        </router-link>
        <router-link to="/catalog?category=oils" class="text-sm font-medium text-muted hover:text-dark transition-colors">
          Oils
        </router-link>
      </nav>

      <div class="flex items-center gap-2">
        <button
          class="p-2 hover:bg-primary/30 rounded-lg transition-colors"
          @click="isSearchVisible = !isSearchVisible"
          aria-label="Search"
        >
          <Search class="w-5 h-5 text-dark" />
        </button>

        <router-link
          :to="userStore.isAuthenticated ? '/account' : '/auth/login'"
          class="p-2 hover:bg-primary/30 rounded-lg transition-colors"
          aria-label="Account"
        >
          <User class="w-5 h-5 text-dark" />
        </router-link>

        <button
          class="p-2 hover:bg-primary/30 rounded-lg transition-colors relative"
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

    <div
      v-if="isSearchVisible"
      class="border-t border-primary/20 px-4 py-3"
    >
      <div class="max-w-2xl mx-auto relative">
        <Search class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search products..."
          class="w-full pl-11 pr-4 py-3 bg-white border border-primary/40 rounded-lg text-sm focus:outline-none focus:border-gold transition-colors"
          @keyup.enter="handleSearch"
        />
      </div>
    </div>

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
