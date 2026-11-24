<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import BaseSelect from '@/components/base/BaseSelect.vue'
import { orderService } from '@/services/order.service'
import type { AdminOrder } from '@/types'

const orders = ref<AdminOrder[]>([])
const loading = ref(true)
const statusFilter = ref('')
const updatingId = ref<string | null>(null)
const errorMessage = ref('')

const statusLabels: Record<string, string> = {
  awaiting_payment: 'Awaiting Payment',
  paid: 'Paid',
  processing: 'Processing',
  dispatched: 'Dispatched',
  delivered: 'Delivered',
  cancelled: 'Cancelled',
}

const statusOptions = [
  { value: '', label: 'All Statuses' },
  { value: 'awaiting_payment', label: 'Awaiting Payment' },
  { value: 'paid', label: 'Paid' },
  { value: 'processing', label: 'Processing' },
  { value: 'dispatched', label: 'Dispatched' },
  { value: 'delivered', label: 'Delivered' },
  { value: 'cancelled', label: 'Cancelled' },
]

const transitionOptions: Record<string, { value: string; label: string }[]> = {
  awaiting_payment: [
    { value: 'cancelled', label: 'Cancel' },
  ],
  paid: [
    { value: 'processing', label: 'Start Processing' },
  ],
  processing: [
    { value: 'dispatched', label: 'Mark Dispatched' },
  ],
  dispatched: [
    { value: 'delivered', label: 'Mark Delivered' },
  ],
  delivered: [],
  cancelled: [],
}

async function loadOrders() {
  loading.value = true
  errorMessage.value = ''
  try {
    const params: { page?: number; status?: string } = {}
    if (statusFilter.value) params.status = statusFilter.value
    const data = await orderService.getAllOrders(params)
    orders.value = data.results
  } catch {
    orders.value = []
    errorMessage.value = 'Could not load orders. Please try again.'
  } finally {
    loading.value = false
  }
}

async function updateStatus(order: AdminOrder, newStatus: string) {
  updatingId.value = order.id
  errorMessage.value = ''
  try {
    const updated = await orderService.updateOrderStatus(order.id, newStatus)
    const idx = orders.value.findIndex(o => o.id === order.id)
    if (idx !== -1) orders.value[idx] = updated
  } catch (e: unknown) {
    errorMessage.value = (e as { response?: { data?: { detail?: string } } }).response?.data?.detail
      || 'Could not update order status. Please try again.'
  } finally {
    updatingId.value = null
  }
}

onMounted(loadOrders)
</script>

<template>
  <AdminLayout>
    <div>
      <div class="flex items-center justify-between mb-6">
        <h1 class="font-heading text-xl font-semibold">Orders</h1>
        <div class="w-48">
          <BaseSelect
            v-model="statusFilter"
            :options="statusOptions"
            placeholder="All Statuses"
            @update:model-value="loadOrders"
          />
        </div>
      </div>

      <div
        v-if="errorMessage"
        role="alert"
        class="mb-4 flex items-center justify-between gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
      >
        <span>{{ errorMessage }}</span>
        <button
          type="button"
          class="shrink-0 font-semibold underline underline-offset-2 hover:text-red-900"
          @click="errorMessage = ''"
        >
          Dismiss
        </button>
      </div>

      <div v-if="loading" class="bg-white rounded-[16px] border border-gray-100 overflow-hidden">
        <div class="p-8 text-center text-gray-400">Loading...</div>
      </div>

      <div v-else class="bg-white rounded-[16px] border border-gray-100 overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-100">
              <th class="text-left px-4 py-3 font-medium text-gray-500">Order</th>
              <th class="text-left px-4 py-3 font-medium text-gray-500 hidden md:table-cell">Customer</th>
              <th class="text-left px-4 py-3 font-medium text-gray-500">Status</th>
              <th class="text-left px-4 py-3 font-medium text-gray-500">Total</th>
              <th class="text-left px-4 py-3 font-medium text-gray-500 hidden md:table-cell">Date</th>
              <th class="text-right px-4 py-3 font-medium text-gray-500">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in orders" :key="order.id" class="border-b border-gray-50 hover:bg-gray-50">
              <td class="px-4 py-3 font-mono text-xs">{{ order.id.slice(0, 8) }}...</td>
              <td class="px-4 py-3 hidden md:table-cell">{{ order.user_name || 'N/A' }}</td>
              <td class="px-4 py-3">
                <span class="inline-block px-2 py-1 text-xs rounded-full font-medium" :class="{
                  'bg-yellow-100 text-yellow-700': order.status === 'awaiting_payment',
                  'bg-green-100 text-green-700': order.status === 'paid' || order.status === 'delivered',
                  'bg-blue-100 text-blue-700': order.status === 'processing' || order.status === 'dispatched',
                  'bg-red-100 text-red-700': order.status === 'cancelled',
                }">
                  {{ statusLabels[order.status] || order.status }}
                </span>
              </td>
              <td class="px-4 py-3">K{{ order.grand_total }}</td>
              <td class="px-4 py-3 text-gray-500 hidden md:table-cell">{{ new Date(order.created_at).toLocaleDateString() }}</td>
              <td class="px-4 py-3 text-right">
                <BaseSelect
                  v-if="transitionOptions[order.status]?.length"
                  model-value=""
                  size="sm"
                  align="right"
                  :placeholder="updatingId === order.id ? 'Updating...' : 'Change status'"
                  :aria-label="`Change status for order ${order.id.slice(0, 8)}`"
                  :options="transitionOptions[order.status]!"
                  :disabled="updatingId === order.id"
                  class="inline-block w-36 text-left"
                  @update:model-value="(val) => updateStatus(order, val)"
                />
                <span v-else class="text-xs text-gray-400">No actions</span>
              </td>
            </tr>
            <tr v-if="orders.length === 0">
              <td colspan="6" class="px-4 py-8 text-center text-gray-400">No orders found.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AdminLayout>
</template>
