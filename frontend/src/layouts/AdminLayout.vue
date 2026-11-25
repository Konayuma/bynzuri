<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { LayoutDashboard, Package, ShoppingCart, Truck, LogOut, Menu, Tag, Store, ArrowLeft } from '@lucide/vue'

const router = useRouter()
const userStore = useUserStore()
const sidebarOpen = ref(false)

const navItems = [
  { label: 'Dashboard', icon: LayoutDashboard, to: '/admin' },
  { label: 'Products', icon: Package, to: '/admin/products' },
  { label: 'Discounts', icon: Tag, to: '/admin/discounts' },
  { label: 'Orders', icon: ShoppingCart, to: '/admin/orders' },
  { label: 'Delivery', icon: Truck, to: '/admin/delivery' }
]

function handleLogout() {
  userStore.logout()
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex">
    <aside
      class="fixed inset-y-0 left-0 z-40 w-64 bg-white border-r border-gray-200 transform transition-transform lg:translate-x-0 lg:static"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div class="p-4 border-b border-gray-100">
        <router-link to="/" aria-label="By Nzuri home" class="block w-32 h-20 -ml-4 -my-3"><img src="/By%20Nzuri%20Vector%20Logo%20-01.svg" alt="By Nzuri" class="w-full h-full object-contain" /></router-link>
        <p class="text-xs text-gray-400">Admin Dashboard</p>
      </div>
      <nav aria-label="Admin navigation" class="p-3 space-y-1">
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 px-3 py-2.5 text-sm rounded-lg transition-colors"
          :class="$route.path === item.to ? 'bg-gray-100 text-dark font-medium' : 'text-gray-500 hover:text-dark hover:bg-gray-50'"
          @click="sidebarOpen = false"
        >
          <component :is="item.icon" class="w-4 h-4" />
          {{ item.label }}
        </router-link>
      </nav>
      <div class="absolute bottom-0 left-0 right-0 p-3 border-t border-gray-100 space-y-1">
        <router-link
          to="/"
          class="flex items-center gap-3 px-3 py-2.5 text-sm text-gray-600 hover:text-dark rounded-lg hover:bg-gray-50 w-full transition-colors focus-visible:outline-2 focus-visible:outline-gold"
          @click="sidebarOpen = false"
        >
          <Store class="w-4 h-4" />
          Back to Site
        </router-link>
        <button
          class="flex items-center gap-3 px-3 py-2.5 text-sm text-gray-500 hover:text-red-500 rounded-lg hover:bg-red-50 w-full transition-colors"
          @click="handleLogout"
        >
          <LogOut class="w-4 h-4" />
          Sign Out
        </button>
      </div>
    </aside>

    <div v-if="sidebarOpen" class="fixed inset-0 bg-black/20 z-30 lg:hidden" @click="sidebarOpen = false" />

    <div class="flex-1 flex flex-col min-w-0">
      <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 lg:px-6">
        <button aria-label="Open admin navigation" :aria-expanded="sidebarOpen" class="lg:hidden p-2 -ml-2" @click="sidebarOpen = true">
          <Menu class="w-5 h-5" />
        </button>
        <router-link
          to="/"
          class="ml-auto inline-flex items-center gap-2 min-h-10 px-3.5 rounded-lg border border-gray-200 text-sm font-medium text-dark hover:bg-gray-50 transition-colors focus-visible:outline-2 focus-visible:outline-gold"
        >
          <ArrowLeft class="w-4 h-4" />
          <span>Back to Site</span>
        </router-link>
      </header>
      <main class="flex-1 p-4 lg:p-6 overflow-auto">
        <slot />
      </main>
    </div>
  </div>
</template>
