<script setup lang="ts">
import AdminLayout from '@/layouts/AdminLayout.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import { Plus } from '@lucide/vue'
</script>

<template>
  <AdminLayout>
    <div>
      <div class="flex items-center justify-between mb-6">
        <h1 class="font-heading text-xl font-semibold">Products</h1>
        <BaseButton size="sm">
          <Plus class="w-4 h-4 mr-1" /> Add Product
        </BaseButton>
      </div>
      <div class="bg-white rounded-[16px] border border-gray-100 overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-100">
              <th class="text-left px-4 py-3 font-medium text-gray-500">Product</th>
              <th class="text-left px-4 py-3 font-medium text-gray-500 hidden md:table-cell">Category</th>
              <th class="text-left px-4 py-3 font-medium text-gray-500">Price</th>
              <th class="text-left px-4 py-3 font-medium text-gray-500 hidden md:table-cell">Stock</th>
              <th class="text-right px-4 py-3 font-medium text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr class="border-b border-gray-50">
              <td colspan="5" class="px-4 py-8 text-center text-gray-400">
                No products yet. Add your first product.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AdminLayout>
</template>
