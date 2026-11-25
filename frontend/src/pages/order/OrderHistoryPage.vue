<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { orderService } from '@/services/order.service'
import BaseButton from '@/components/base/BaseButton.vue'
import { Package } from '@lucide/vue'
import type { Order } from '@/types'

const orders = ref<Order[]>([])
const loading = ref(true)
const error = ref(false)

const statusColors: Record<string, string> = {
  awaiting_payment: 'text-gold bg-gold/10',
  paid: 'text-blue-500 bg-blue-50',
  processing: 'text-dark bg-primary/30',
  dispatched: 'text-success bg-success/10',
  delivered: 'text-success bg-success/10',
  cancelled: 'text-red-500 bg-red-50'
}

const statusLabels: Record<string, string> = {
  awaiting_payment: 'Awaiting Payment',
  paid: 'Paid',
  processing: 'Processing',
  dispatched: 'Dispatched',
  delivered: 'Delivered',
  cancelled: 'Cancelled'
}

async function loadOrders() {
  loading.value = true
  error.value = false
  try {
    orders.value = await orderService.getOrders()
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}
onMounted(loadOrders)
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <h1 class="font-heading text-2xl font-semibold text-dark mb-6">Order History</h1>

    <div v-if="loading" class="space-y-4" role="status" aria-live="polite">
      <p class="text-sm text-muted">Loading your orders…</p>
      <div v-for="i in 3" :key="i" class="bg-white rounded-[20px] p-6 shadow-[0_8px_30px_rgba(0,0,0,0.06)]">
        <div class="h-4 w-32 bg-primary/30 rounded animate-pulse mb-3" />
        <div class="h-3 w-48 bg-primary/30 rounded animate-pulse" />
      </div>
    </div>

    <div v-else-if="error" class="rounded-[20px] border border-primary/40 bg-white p-6 text-center" role="alert">
      <p class="font-medium text-dark">We couldn’t load your orders.</p>
      <p class="mt-2 text-sm text-muted">Check your connection and try again.</p>
      <BaseButton class="mt-4" variant="outline" @click="loadOrders">Try again</BaseButton>
    </div>

    <div v-else-if="orders.length === 0" class="text-center py-16">
      <div class="w-16 h-16 rounded-full bg-primary/40 flex items-center justify-center mx-auto mb-4">
        <Package class="w-8 h-8 text-muted" />
      </div>
      <p class="text-dark font-medium mb-1">No orders yet</p>
      <p class="text-sm text-muted mb-4">Once you place an order, it'll show up here.</p>
      <router-link to="/catalog">
        <BaseButton variant="outline">Browse Products</BaseButton>
      </router-link>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="order in orders"
        :key="order.id"
        class="bg-white rounded-[20px] p-5 shadow-[0_8px_30px_rgba(0,0,0,0.06)]"
      >
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs font-mono text-muted">
            #{{ order.id.slice(0, 8).toUpperCase() }}
          </span>
          <span
            class="text-xs font-medium px-2.5 py-1 rounded-full capitalize"
            :class="statusColors[order.status] || 'text-muted bg-primary/20'"
          >
            {{ statusLabels[order.status] || order.status.replace('_', ' ') }}
          </span>
        </div>
        <div class="flex items-center justify-between text-sm">
          <span class="text-muted">{{ new Date(order.created_at).toLocaleDateString('en-ZM', { year: 'numeric', month: 'short', day: 'numeric' }) }}</span>
          <span class="font-semibold text-dark tabular-nums">K{{ order.grand_total }}</span>
        </div>
        <ul v-if="order.items.length > 0" class="mt-3 space-y-1 border-t border-primary/15 pt-3 text-xs text-muted">
          <li v-for="item in order.items.slice(0, 3)" :key="item.id" class="flex justify-between gap-2">
            <span class="truncate text-dark">{{ item.product_title }}</span>
            <span class="shrink-0 tabular-nums">× {{ item.quantity }}</span>
          </li>
          <li v-if="order.items.length > 3" class="text-muted">+ {{ order.items.length - 3 }} more {{ order.items.length - 3 === 1 ? 'item' : 'items' }}</li>
        </ul>
        <div class="mt-3 flex items-center justify-between pt-1">
          <span class="text-xs text-muted">
            {{ order.items.length }} item{{ order.items.length !== 1 ? 's' : '' }}
          </span>
          <router-link :to="`/order/confirmation/${order.id}`" class="inline-flex min-h-10 items-center text-sm font-medium underline underline-offset-4 text-dark hover:text-gold transition-colors">
            View order
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>
