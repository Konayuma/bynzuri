<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import { adminService } from '@/services/admin.service'
import type { DashboardStats } from '@/types'

const stats = ref<DashboardStats | null>(null)
const loading = ref(true)
const error = ref('')

const statusLabels: Record<string, string> = {
  awaiting_payment: 'Awaiting Payment',
  paid: 'Paid',
  processing: 'Processing',
  dispatched: 'Dispatched',
  delivered: 'Delivered',
  cancelled: 'Cancelled',
}

onMounted(async () => {
  try {
    stats.value = await adminService.getDashboard()
  } catch {
    error.value = 'Failed to load dashboard data'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <AdminLayout>
    <div>
      <h1 class="font-heading text-xl font-semibold mb-6">Dashboard</h1>

      <div v-if="loading" class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div v-for="i in 4" :key="i" class="bg-white rounded-[16px] p-4 border border-gray-100 animate-pulse">
          <div class="h-3 bg-gray-200 rounded w-16 mb-2" />
          <div class="h-6 bg-gray-200 rounded w-20" />
        </div>
      </div>

      <div v-else-if="error" class="bg-red-50 text-red-600 p-4 rounded-[16px] text-sm">
        {{ error }}
      </div>

      <template v-else-if="stats">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div class="bg-white rounded-[16px] p-4 border border-gray-100">
            <p class="text-xs text-gray-500 uppercase tracking-wide">Revenue</p>
            <p class="text-xl font-bold text-dark mt-1">K{{ stats.revenue }}</p>
          </div>
          <div class="bg-white rounded-[16px] p-4 border border-gray-100">
            <p class="text-xs text-gray-500 uppercase tracking-wide">Orders</p>
            <p class="text-xl font-bold text-dark mt-1">{{ stats.orders }}</p>
          </div>
          <div class="bg-white rounded-[16px] p-4 border border-gray-100">
            <p class="text-xs text-gray-500 uppercase tracking-wide">Products</p>
            <p class="text-xl font-bold text-dark mt-1">{{ stats.products }}</p>
          </div>
          <div class="bg-white rounded-[16px] p-4 border border-gray-100">
            <p class="text-xs text-gray-500 uppercase tracking-wide">Customers</p>
            <p class="text-xl font-bold text-dark mt-1">{{ stats.customers }}</p>
          </div>
        </div>

        <div class="grid md:grid-cols-2 gap-6">
          <div class="bg-white rounded-[16px] border border-gray-100 p-4">
            <h2 class="font-heading text-base font-semibold mb-3">Orders by Status</h2>
            <div class="space-y-2">
              <div v-for="item in stats.orders_by_status" :key="item.status" class="flex items-center justify-between text-sm">
                <span class="text-gray-600">{{ statusLabels[item.status] || item.status }}</span>
                <span class="font-medium">{{ item.count }}</span>
              </div>
              <div v-if="stats.orders_by_status.length === 0" class="text-sm text-gray-400 text-center py-4">
                No orders yet
              </div>
            </div>
          </div>

          <div class="bg-white rounded-[16px] border border-gray-100 p-4">
            <h2 class="font-heading text-base font-semibold mb-3">Low Stock Alerts</h2>
            <div class="space-y-2">
              <div v-for="item in stats.low_stock" :key="item.id" class="flex items-center justify-between text-sm">
                <span class="text-gray-600 truncate">{{ item.title }}</span>
                <span class="font-medium text-red-500">{{ item.stock }} left</span>
              </div>
              <div v-if="stats.low_stock.length === 0" class="text-sm text-gray-400 text-center py-4">
                All products well stocked
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-[16px] border border-gray-100 mt-6 overflow-hidden">
          <div class="p-4 border-b border-gray-100">
            <h2 class="font-heading text-base font-semibold">Recent Orders</h2>
          </div>
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-100">
                <th class="text-left px-4 py-3 font-medium text-gray-500">Order</th>
                <th class="text-left px-4 py-3 font-medium text-gray-500 hidden md:table-cell">Total</th>
                <th class="text-left px-4 py-3 font-medium text-gray-500">Status</th>
                <th class="text-left px-4 py-3 font-medium text-gray-500 hidden md:table-cell">Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in stats.recent_orders" :key="order.id" class="border-b border-gray-50 hover:bg-gray-50">
                <td class="px-4 py-3 font-mono text-xs">{{ order.id.slice(0, 8) }}...</td>
                <td class="px-4 py-3 hidden md:table-cell">K{{ order.grand_total }}</td>
                <td class="px-4 py-3">
                  <span class="inline-block px-2 py-1 text-xs rounded-full" :class="{
                    'bg-yellow-100 text-yellow-700': order.status === 'awaiting_payment',
                    'bg-green-100 text-green-700': order.status === 'paid' || order.status === 'delivered',
                    'bg-blue-100 text-blue-700': order.status === 'processing' || order.status === 'dispatched',
                    'bg-red-100 text-red-700': order.status === 'cancelled',
                  }">
                    {{ statusLabels[order.status] || order.status }}
                  </span>
                </td>
                <td class="px-4 py-3 text-gray-500 hidden md:table-cell">{{ new Date(order.created_at).toLocaleDateString() }}</td>
              </tr>
              <tr v-if="stats.recent_orders.length === 0">
                <td colspan="4" class="px-4 py-8 text-center text-gray-400">No orders yet</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>
  </AdminLayout>
</template>
