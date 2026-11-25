<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search, X, ImageOff } from '@lucide/vue'
import { productService } from '@/services/product.service'
import { signatureImage } from '@/utils/productImage'
import type { Product } from '@/types'

const props = defineProps<{ modelValue: string; mobile?: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [value: string]; submit: [] }>()
const router = useRouter()
const route = useRoute()
const root = ref<HTMLElement | null>(null)
const input = ref<HTMLInputElement | null>(null)
const open = ref(false)
const loading = ref(false)
const failed = ref(false)
const results = ref<Product[]>([])
const activeIndex = ref(-1)
const query = computed(() => props.modelValue.trim())
const listId = computed(() => props.mobile ? 'mobile-search-results' : 'desktop-search-results')
let timer: ReturnType<typeof setTimeout> | undefined
let requestId = 0

function close() {
  open.value = false
  activeIndex.value = -1
  clearTimeout(timer)
  requestId++
  loading.value = false
}
function search() {
  clearTimeout(timer)
  const current = ++requestId
  results.value = []
  failed.value = false
  activeIndex.value = -1
  if (!open.value || !query.value) { loading.value = false; return }
  loading.value = true
  const searchTerm = query.value
  timer = setTimeout(async () => {
    try {
      const response = await productService.getProducts({ search: searchTerm })
      if (current === requestId) results.value = response.results.slice(0, 5)
    } catch {
      if (current === requestId) failed.value = true
    } finally {
      if (current === requestId) loading.value = false
    }
  }, 250)
}
watch(() => props.modelValue, search)
watch(() => route.fullPath, close)
function focusSearch() { open.value = true; search() }
function onOutside(event: PointerEvent) { if (!root.value?.contains(event.target as Node)) close() }
function clear() { emit('update:modelValue', ''); input.value?.focus() }
function submit() { close(); emit('submit') }
function choose(product: Product) { close(); router.push({ name: 'product-detail', params: { slug: product.slug } }) }
function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') { if (open.value) { event.stopPropagation(); close() }; return }
  if (event.key === 'ArrowDown' && results.value.length) { event.preventDefault(); open.value = true; activeIndex.value = Math.min(activeIndex.value + 1, results.value.length - 1) }
  if (event.key === 'ArrowUp' && results.value.length) { event.preventDefault(); activeIndex.value = Math.max(activeIndex.value - 1, -1) }
  if (event.key === 'Enter') { event.preventDefault(); if (open.value && activeIndex.value >= 0 && results.value[activeIndex.value]) choose(results.value[activeIndex.value]!); else submit() }
}
function productImage(product: Product) { return product.images?.find(image => image.is_primary)?.image || product.images?.[0]?.image || signatureImage(product.slug) }
onMounted(() => { document.addEventListener('pointerdown', onOutside); if (props.mobile) nextTick(() => input.value?.focus()) })
onBeforeUnmount(() => { clearTimeout(timer); requestId++; document.removeEventListener('pointerdown', onOutside) })
</script>

<template>
  <div ref="root" class="product-search" @focusout="(event) => { if (event.relatedTarget && !root?.contains(event.relatedTarget as Node)) close() }">
    <div class="search-field">
      <button type="button" class="search-submit" aria-label="Submit search" @click="submit"><Search :size="17" /></button>
      <input ref="input" :id="mobile ? 'mobile-product-search' : undefined" :value="modelValue" type="search" role="combobox" aria-label="Search products" aria-autocomplete="list" :aria-expanded="open && !!query" :aria-controls="listId" :aria-activedescendant="activeIndex >= 0 && open ? `${listId}-${activeIndex}` : undefined" placeholder="Search products..." autocomplete="off" @input="emit('update:modelValue', ($event.target as HTMLInputElement).value); open = true" @focus="focusSearch" @keydown="onKeydown" />
      <button v-if="modelValue" type="button" class="search-clear" aria-label="Clear search" @click="clear"><X :size="16" /></button>
    </div>
    <div v-if="open && query" class="search-panel">
      <p v-if="loading" class="search-message" role="status">Searching products…</p>
      <p v-else-if="failed" class="search-message" role="status">Search is unavailable. Please try again.</p>
      <p v-else-if="!results.length" class="search-message" role="status">No products found for “{{ query }}”.</p>
      <template v-else>
        <p class="search-label">Products</p>
        <ul :id="listId" role="listbox" aria-label="Product suggestions">
          <li v-for="(product, index) in results" :id="`${listId}-${index}`" :key="product.id" role="option" :aria-selected="activeIndex === index">
            <button type="button" class="search-result" :class="{ 'is-active': activeIndex === index }" @mouseenter="activeIndex = index" @click="choose(product)">
              <span class="result-image"><img v-if="productImage(product)" :src="productImage(product)" alt="" /><ImageOff v-else :size="18" /></span>
              <span class="result-details"><strong>{{ product.title }}</strong><span>{{ product.category_name }}</span></span>
              <span class="result-price"><span v-if="Number(product.effective_discount_percent ?? product.discount_percent) > 0" class="mr-2 line-through">K{{ product.price }}</span>K{{ product.sale_price ?? product.price }}</span>
            </button>
          </li>
        </ul>
      </template>
      <button v-if="!failed && !loading" type="button" class="search-all" @click="submit">View all results <span aria-hidden="true">↗</span></button>
    </div>
  </div>
</template>

<style scoped>
.product-search{position:relative;width:100%}.search-field{position:relative;display:flex;align-items:center}.search-field input{width:100%;height:42px;padding:0 42px;border:1px solid transparent;border-radius:999px;background:#f5eeee;color:#302526;font-size:16px;outline:none;transition:background .15s,border-color .15s}.search-field input:focus{background:#fff;border-color:#cbaeb1}.search-field input::placeholder{color:#8c7d7f}.search-field input::-webkit-search-cancel-button{display:none}.search-submit,.search-clear{position:absolute;z-index:1;display:grid;place-items:center;width:40px;height:40px;color:#756668;border-radius:50%}.search-submit{left:2px}.search-clear{right:2px}.search-submit:focus-visible,.search-clear:focus-visible,.search-result:focus-visible,.search-all:focus-visible{outline:2px solid #875e64;outline-offset:-2px}.search-panel{position:absolute;top:calc(100% + 9px);left:0;right:0;z-index:20;max-height:min(70vh,480px);overflow:auto;padding:8px;background:#fffdfc;border:1px solid #eadcdd;border-radius:18px;box-shadow:0 18px 45px rgba(50,30,33,.14)}.search-message{padding:16px 12px;color:#67585a;font-size:14px}.search-label{padding:8px 10px;color:#776669;font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase}.search-result{display:flex;align-items:center;gap:12px;width:100%;padding:8px;border-radius:11px;text-align:left;color:#302526}.search-result:hover,.search-result.is-active{background:#f8eff0}.result-image{display:grid;place-items:center;flex:none;width:48px;height:48px;border-radius:9px;background:#f8f1f0;color:#8d7b7d;overflow:hidden}.result-image img{width:100%;height:100%;object-fit:contain}.result-details{min-width:0;flex:1}.result-details strong,.result-details span{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.result-details strong{font-size:14px;font-weight:600}.result-details span{margin-top:3px;color:#78696b;font-size:12px}.result-price{flex:none;font-size:13px;font-weight:600}.search-all{display:flex;justify-content:space-between;width:100%;padding:13px 10px;border-top:1px solid #f1e7e7;color:#63474c;font-size:14px;font-weight:600}.search-all:hover{color:#2e2022}@media(min-width:1024px){.search-field input{font-size:14px}}
</style>
