<script setup lang="ts">
import AdminLayout from '@/layouts/AdminLayout.vue'
</script>

<template>
  <AdminLayout>
    <div>
      <h1 class="font-heading text-xl font-semibold mb-6">Orders</h1>
      <div class="bg-white rounded-[16px] border border-gray-100 overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-100">
              <th class="text-left px-4 py-3 font-medium text-gray-500">Order</th>
              <th class="text-left px-4 py-3 font-medium text-gray-500 hidden md:table-cell">Customer</th>
              <th class="text-left px-4 py-3 font-medium text-gray-500">Status</th>
              <th class="text-left px-4 py-3 font-medium text-gray-500">Total</th>
              <th class="text-right px-4 py-3 font-medium text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr class="border-b border-gray-50">
              <td colspan="5" class="px-4 py-8 text-center text-gray-400">
                No orders yet.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AdminLayout>
</template>
