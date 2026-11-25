<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { productService, type SaleCampaign } from '@/services/product.service'

defineProps<{ compact?: boolean }>()
const campaign = ref<SaleCampaign | null>(null)
const dateLabel = computed(() => {
  if (!campaign.value) return ''
  const date = (value: string) => new Date(`${value}T12:00:00Z`)
  const ordinal = (day: number) => `${day}${day % 100 >= 11 && day % 100 <= 13 ? 'th' : ({ 1: 'st', 2: 'nd', 3: 'rd' } as Record<number, string>)[day % 10] || 'th'}`
  const start = date(campaign.value.starts_on); const end = date(campaign.value.ends_on)
  const month = (value: Date) => new Intl.DateTimeFormat('en-GB', { month: 'long', timeZone: 'UTC' }).format(value)
  return start.getUTCFullYear() === end.getUTCFullYear() && start.getUTCMonth() === end.getUTCMonth()
    ? `${ordinal(start.getUTCDate())} – ${ordinal(end.getUTCDate())} ${month(end)}`
    : `${ordinal(start.getUTCDate())} ${month(start)} – ${ordinal(end.getUTCDate())} ${month(end)}`
})
onMounted(async () => { try { campaign.value = await productService.getCampaign() } catch { /* Storefront remains usable if the announcement is unavailable. */ } })
</script>

<template>
  <section v-if="campaign" aria-label="Sale announcement" class="sale-banner" :class="{ 'sale-banner--compact': compact }">
    <div class="sale-banner__inner">
      <div class="sale-banner__title"><span class="sale-banner__eyebrow">A little something special</span><h2>{{ campaign.title }}</h2></div>
      <p class="sale-banner__offer">{{ Number(campaign.percent) }}<span>% off</span></p>
      <div class="sale-banner__details"><p>{{ dateLabel }}</p><p>{{ campaign.fulfilment }}</p></div>
      <router-link v-if="!compact" to="/catalog" class="sale-banner__link">Explore the collection <span aria-hidden="true">↗</span></router-link>
    </div>
  </section>
</template>

<style scoped>
.sale-banner{background:#2a1d20;color:#fff7f3;overflow:hidden}
.sale-banner__inner{max-width:1280px;margin:auto;padding:1.5rem 2rem;display:flex;gap:2rem;align-items:center;justify-content:space-between}
.sale-banner__title{min-width:0}.sale-banner__eyebrow{display:block;color:#e6bab9;font-size:.7rem;letter-spacing:.17em;text-transform:uppercase;font-weight:600}.sale-banner h2{font-family:var(--font-heading,serif);font-size:clamp(1.55rem,3vw,2.4rem);line-height:1.15;margin:.35rem 0 0;overflow-wrap:anywhere}
.sale-banner__offer{font-family:var(--font-heading,serif);font-size:clamp(3rem,6vw,5rem);line-height:.9;white-space:nowrap;color:#f4c6c2}.sale-banner__offer span{font-size:.32em;margin-left:.18em;text-transform:uppercase;letter-spacing:.06em}
.sale-banner__details{font-size:.875rem;line-height:1.65;color:#fff1ed}.sale-banner__details p+p{color:#e6bab9}.sale-banner__link{color:#fff7f3;min-height:44px;display:inline-flex;align-items:center;gap:.5rem;font-size:.875rem;text-decoration:underline;text-underline-offset:5px;white-space:nowrap}.sale-banner__link:focus-visible{outline:2px solid #f4c6c2;outline-offset:4px}
.sale-banner--compact{border-radius:1.25rem;margin-bottom:2rem}.sale-banner--compact .sale-banner__inner{padding:1.25rem 1.75rem}
@media(max-width:700px){.sale-banner__inner{padding:1.4rem 1.25rem;display:grid;grid-template-columns:1fr auto;gap:1rem}.sale-banner__details{grid-column:1/-1}.sale-banner__link{grid-column:1/-1}.sale-banner__offer{font-size:3.5rem}.sale-banner--compact .sale-banner__inner{padding:1.3rem}}
</style>
