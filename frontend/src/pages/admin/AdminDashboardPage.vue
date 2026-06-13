<script setup lang="ts">
import AdminLayout from '@/layouts/AdminLayout.vue'
</script>

<template>
  <AdminLayout>
    <div>
      <h1 class="font-heading text-xl font-semibold mb-6">Dashboard</h1>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-white rounded-[16px] p-4 border border-gray-100">
          <p class="text-xs text-gray-500 uppercase tracking-wide">Revenue</p>
          <p class="text-xl font-bold text-dark mt-1">K0</p>
        </div>
        <div class="bg-white rounded-[16px] p-4 border border-gray-100">
          <p class="text-xs text-gray-500 uppercase tracking-wide">Orders</p>
          <p class="text-xl font-bold text-dark mt-1">0</p>
        </div>
        <div class="bg-white rounded-[16px] p-4 border border-gray-100">
          <p class="text-xs text-gray-500 uppercase tracking-wide">Products</p>
          <p class="text-xl font-bold text-dark mt-1">0</p>
        </div>
        <div class="bg-white rounded-[16px] p-4 border border-gray-100">
          <p class="text-xs text-gray-500 uppercase tracking-wide">Customers</p>
          <p class="text-xl font-bold text-dark mt-1">0</p>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>
