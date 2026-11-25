<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import { productService } from '@/services/product.service'
import CampaignEditor from '@/components/admin/CampaignEditor.vue'

const percent = ref('0')
const saved = ref('0')
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const loadFailed = ref(false)
const message = ref('')
const preview = computed(() => (100 * (1 - (Number(percent.value) || 0) / 100)).toFixed(2))

async function load() {
  loading.value = true
  error.value = ''; loadFailed.value = false
  try { percent.value = (await productService.getStoreDiscount()).percent; saved.value = percent.value }
  catch { error.value = 'Could not load the discount. Please try again.'; loadFailed.value = true }
  finally { loading.value = false }
}
async function save() {
  const value = percent.value.trim()
  if (!/^\d+(\.\d{1,2})?$/.test(value) || Number(value) > 100) {
    error.value = 'Enter a percentage between 0 and 100, with up to two decimal places.'
    return
  }
  saving.value = true; error.value = ''; message.value = ''
  try {
    percent.value = (await productService.setStoreDiscount(value)).percent
    saved.value = percent.value
    message.value = Number(percent.value) ? 'Storewide discount is active.' : 'Storewide discount has been removed.'
  } catch { error.value = 'Could not save the discount. Please check your connection and try again.' }
  finally { saving.value = false }
}
onMounted(load)
</script>

<template>
  <AdminLayout>
    <div class="mx-auto max-w-4xl space-y-6">
      <header><p class="text-xs font-semibold uppercase tracking-widest text-rose-700">Pricing</p><h1 class="mt-2 font-serif text-3xl text-gray-900">Discounts</h1><p class="mt-2 text-sm text-gray-600">Manage an offer across your entire collection.</p></header>
      <CampaignEditor />
      <div v-if="loading" role="status" class="text-sm text-gray-600">Loading discount…</div>
      <div v-else-if="loadFailed" role="alert" class="text-sm text-red-700">{{ error }} <button type="button" class="underline" @click="load">Retry</button></div>
      <div v-else class="grid gap-5 md:grid-cols-[1fr_0.75fr]">
        <form class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm" @submit.prevent="save">
          <div class="flex items-center justify-between gap-4"><h2 class="font-serif text-xl text-gray-900">Storewide offer</h2><span class="rounded-full bg-rose-50 px-3 py-1 text-xs font-semibold text-rose-800">{{ Number(saved) ? `${Number(saved)}% active` : 'No active offer' }}</span></div>
          <p class="mt-3 mb-5 text-sm leading-6 text-gray-600">Apply a percentage discount to every product, including products added later.</p>
          <BaseInput v-model="percent" label="Discount percentage" type="number" min="0" max="100" step="0.01" hint="Enter 0 to remove the storewide offer." required />
          <p v-if="error" role="alert" class="mt-3 text-sm text-red-700">{{ error }}</p>
          <p v-if="message" role="status" class="mt-3 text-sm text-green-700">{{ message }}</p>
          <BaseButton type="submit" :loading="saving" class="mt-5">Save discount</BaseButton>
        </form>
        <aside class="rounded-2xl bg-[#efe3e3] p-6 text-gray-900"><p class="text-xs font-semibold uppercase tracking-widest text-rose-800">Price preview</p><p class="mt-5 text-sm text-gray-600">A product priced at K100.00</p><p class="mt-2 font-serif text-3xl">K{{ preview }}</p><p class="mt-2 text-sm text-gray-600">Original price <span class="line-through">K100.00</span></p><div class="mt-6 border-t border-rose-300/60 pt-4 text-sm leading-6 text-gray-700">If a product has its own discount, the larger discount applies. Discounts are not combined.</div></aside>
      </div>
    </div>
  </AdminLayout>
</template>
