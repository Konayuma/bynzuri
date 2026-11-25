<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import AdminLayout from '@/layouts/AdminLayout.vue'
import { adminService } from '@/services/admin.service'
import type { DashboardStats } from '@/types'

const stats = ref<DashboardStats | null>(null)
const loading = ref(true)
const error = ref('')
const days = ref(30)
const refreshing = ref(false)
const money = (value: string | number) => `K${Number(value).toLocaleString('en-ZM', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
const chartSeries = computed(() => [{ name: 'Sales', data: stats.value?.sales_history.map(day => Number(day.revenue)) ?? [] }])
const chartOptions = computed(() => ({
  chart: { toolbar: { show: false }, zoom: { enabled: false }, animations: { enabled: false }, fontFamily: 'inherit' },
  colors: ['#9b666f'], stroke: { curve: 'smooth' as const, width: 3 },
  fill: { type: 'gradient', gradient: { opacityFrom: 0.25, opacityTo: 0.02, stops: [0, 100] } },
  dataLabels: { enabled: false }, grid: { borderColor: '#eee8e8', strokeDashArray: 4 },
  xaxis: { categories: stats.value?.sales_history.map(day => day.date) ?? [], tickAmount: 5, labels: { rotate: 0, formatter: (value: string) => { const parts = value.split('-'); return parts.length === 3 ? `${parts[2]}/${parts[1]}` : value } } },
  yaxis: { labels: { formatter: (value: number) => `K${value.toLocaleString()}` } },
  tooltip: { y: { formatter: (value: number) => money(value) } },
}))

const statusLabels: Record<string, string> = {
  awaiting_payment: 'Awaiting Payment',
  paid: 'Paid',
  processing: 'Processing',
  dispatched: 'Dispatched',
  delivered: 'Delivered',
  cancelled: 'Cancelled',
}

async function loadDashboard() {
  refreshing.value = true
  try {
    stats.value = await adminService.getDashboard(days.value)
    error.value = ''
  } catch {
    error.value = 'Failed to load dashboard data'
  } finally {
    loading.value = false
    refreshing.value = false
  }
}
onMounted(loadDashboard)
</script>

<template>
  <AdminLayout>
    <div>
      <div class="mb-6 flex flex-wrap items-end justify-between gap-4"><div><p class="mb-1 text-xs font-semibold uppercase tracking-[0.16em] text-[#9b666f]">By Nzuri · Admin</p><h1 class="font-heading text-2xl font-semibold">Dashboard</h1><p class="mt-1 text-sm text-gray-500">A clear view of your store.</p></div><router-link to="/admin/orders" class="rounded-full border border-gray-300 bg-white px-4 py-2 text-sm font-medium hover:bg-gray-50">View all orders →</router-link></div>

      <div v-if="loading" class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div v-for="i in 4" :key="i" class="bg-white rounded-[16px] p-4 border border-gray-100 animate-pulse">
          <div class="h-3 bg-gray-200 rounded w-16 mb-2" />
          <div class="h-6 bg-gray-200 rounded w-20" />
        </div>
      </div>

      <div v-else-if="error" class="bg-red-50 text-red-600 p-4 rounded-[16px] text-sm">
        {{ error }} <button class="ml-2 font-semibold underline" @click="loadDashboard">Try again</button>
      </div>

      <template v-else-if="stats">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div class="bg-white rounded-[16px] p-4 border border-gray-100">
            <p class="text-xs text-gray-500 uppercase tracking-wide">Sales · all time</p>
            <p class="text-xl font-bold text-dark mt-1">{{ money(stats.revenue) }}</p>
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

        <div class="mb-6 grid gap-6 xl:grid-cols-[minmax(0,2fr)_minmax(260px,1fr)]">
          <section class="min-w-0 rounded-[20px] border border-gray-100 bg-white p-5 sm:p-6" aria-labelledby="sales-title">
            <div class="flex flex-wrap items-start justify-between gap-4"><div><h2 id="sales-title" class="font-heading text-lg font-semibold">Sales history</h2><p class="mt-1 text-sm text-gray-500">Paid orders by order date, including delivery.</p></div><label class="text-sm text-gray-600">Period <select v-model.number="days" :disabled="refreshing" class="ml-2 rounded-lg border border-gray-200 bg-white px-3 py-2" @change="loadDashboard"><option :value="7">Last 7 days</option><option :value="30">Last 30 days</option><option :value="90">Last 90 days</option></select></label></div>
            <div class="mt-5 flex flex-wrap gap-x-8 gap-y-3"><div><p class="text-xs uppercase tracking-wide text-gray-500">Sales in period</p><p class="mt-1 text-2xl font-semibold tabular-nums">{{ money(stats.period_revenue) }}</p></div><div><p class="text-xs uppercase tracking-wide text-gray-500">Paid orders</p><p class="mt-1 text-2xl font-semibold tabular-nums">{{ stats.period_orders }}</p></div></div>
            <div v-if="stats.period_orders" class="mt-4" aria-hidden="true"><VueApexCharts type="area" height="280" :options="chartOptions" :series="chartSeries" /></div><p v-else class="py-16 text-center text-sm text-gray-500">No paid orders in this period yet.</p>
            <details v-if="stats.period_orders" class="mt-2 text-sm"><summary class="cursor-pointer text-gray-600">View daily sales data</summary><div class="mt-3 max-h-64 overflow-auto"><table class="w-full text-left"><thead><tr><th class="py-2">Date</th><th>Orders</th><th>Sales</th></tr></thead><tbody><tr v-for="day in stats.sales_history" :key="day.date" class="border-t border-gray-100"><td class="py-2">{{ day.date }}</td><td>{{ day.orders }}</td><td>{{ money(day.revenue) }}</td></tr></tbody></table></div></details>
          </section>
          <section class="rounded-[20px] border border-gray-100 bg-white p-5 sm:p-6"><h2 class="font-heading text-lg font-semibold">Top products</h2><p class="mt-1 text-sm text-gray-500">By product sales in this period, excluding delivery.</p><ol v-if="stats.top_products.length" class="mt-5 divide-y divide-gray-100"><li v-for="(product, index) in stats.top_products" :key="product.product_title" class="flex items-center gap-3 py-3"><span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#f7eded] text-xs font-semibold text-[#875c64]">{{ index + 1 }}</span><div class="min-w-0 flex-1"><p class="break-words text-sm font-medium">{{ product.product_title }}</p><p class="text-xs text-gray-500">{{ product.units }} sold</p></div><span class="text-sm font-semibold tabular-nums">{{ money(product.revenue) }}</span></li></ol><p v-else class="py-12 text-center text-sm text-gray-500">Product sales will appear here.</p></section>
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
