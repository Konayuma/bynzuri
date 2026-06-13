<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import BaseButton from '@/components/base/BaseButton.vue'
import { useRouter } from 'vue-router'
import { User, Package, MapPin, LogOut } from '@lucide/vue'

const userStore = useUserStore()
const router = useRouter()

function handleLogout() {
  userStore.logout()
  router.push('/')
}
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <h1 class="font-heading text-2xl font-semibold text-dark mb-6">My Account</h1>

    <div class="bg-white rounded-[20px] p-6 shadow-[0_8px_30px_rgba(0,0,0,0.06)] mb-6">
      <div class="flex items-center gap-4 mb-4">
        <div class="w-14 h-14 rounded-full bg-primary/50 flex items-center justify-center">
          <User class="w-6 h-6 text-dark" />
        </div>
        <div>
          <p class="font-medium text-dark">{{ userStore.user?.first_name }} {{ userStore.user?.last_name }}</p>
          <p class="text-sm text-muted">{{ userStore.user?.email }}</p>
        </div>
      </div>

      <div class="space-y-3">
        <router-link
          to="/account/orders"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-primary/20 transition-colors"
        >
          <Package class="w-4 h-4 text-muted" />
          <span class="text-sm text-dark">Order History</span>
        </router-link>
        <button
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-primary/20 transition-colors w-full text-left"
        >
          <MapPin class="w-4 h-4 text-muted" />
          <span class="text-sm text-dark">Saved Addresses</span>
        </button>
        <button
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-red-50 transition-colors w-full text-left text-red-500"
          @click="handleLogout"
        >
          <LogOut class="w-4 h-4" />
          <span class="text-sm">Sign Out</span>
        </button>
      </div>
    </div>
  </div>
</template>
