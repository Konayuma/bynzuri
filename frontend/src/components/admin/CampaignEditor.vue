<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { productService, type SaleCampaign } from '@/services/product.service'
import BaseInput from '@/components/base/BaseInput.vue'
import BaseButton from '@/components/base/BaseButton.vue'

const campaign = ref<SaleCampaign | null>(null)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const message = ref('')
async function load() {
  loading.value = true; error.value = ''
  try { campaign.value = await productService.getCampaign(true) }
  catch { error.value = 'Could not load the campaign.' }
  finally { loading.value = false }
}
async function save() {
  if (!campaign.value) return
  if (!campaign.value.title.trim() || !campaign.value.starts_on || !campaign.value.ends_on || !campaign.value.fulfilment.trim() || !/^\d+(\.\d{1,2})?$/.test(campaign.value.percent) || Number(campaign.value.percent) > 100 || campaign.value.ends_on < campaign.value.starts_on) {
    error.value = 'Complete all fields, enter a discount from 0 to 100, and choose an end date after the start date.'; return
  }
  saving.value = true; error.value = ''; message.value = ''
  try { campaign.value = await productService.saveCampaign(campaign.value); message.value = 'Campaign saved.' }
  catch { error.value = 'Could not save the campaign. Check your details and try again.' }
  finally { saving.value = false }
}
onMounted(load)
</script>

<template>
  <section class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm" aria-labelledby="campaign-heading">
    <h2 id="campaign-heading" class="font-serif text-xl text-gray-900">Sale banner &amp; schedule</h2>
    <p class="mt-2 text-sm leading-6 text-gray-600">The banner appears on the homepage and shop. Its discount applies automatically from the start through the end date, in Zambia time. The larger of this and any other discount applies.</p>
    <p v-if="loading" role="status" class="mt-4 text-sm">Loading campaign…</p>
    <div v-else-if="!campaign" class="mt-4 text-sm text-red-700" role="alert">{{ error || 'Campaign unavailable.' }} <button class="underline" @click="load">Retry</button></div>
    <form v-else class="mt-5 grid gap-4 sm:grid-cols-2" @submit.prevent="save">
      <BaseInput v-model="campaign.title" label="Campaign title" maxlength="100" required />
      <BaseInput v-model="campaign.percent" label="Discount (%)" type="number" min="0" max="100" step="0.01" required />
      <BaseInput v-model="campaign.starts_on" label="Start date" type="date" required />
      <BaseInput v-model="campaign.ends_on" label="End date" type="date" required />
      <div class="sm:col-span-2"><BaseInput v-model="campaign.fulfilment" label="Fulfilment message" maxlength="160" required /></div>
      <label class="flex min-h-11 items-center gap-3 text-sm text-gray-800 sm:col-span-2"><input v-model="campaign.enabled" type="checkbox" class="h-4 w-4 accent-rose-700" />Enable campaign and banner</label>
      <p v-if="error" role="alert" class="text-sm text-red-700 sm:col-span-2">{{ error }}</p>
      <p v-if="message" role="status" class="text-sm text-green-700 sm:col-span-2">{{ message }}</p>
      <div class="sm:col-span-2"><BaseButton type="submit" :loading="saving">Save campaign</BaseButton></div>
    </form>
  </section>
</template>
