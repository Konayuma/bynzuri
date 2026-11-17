<script setup lang="ts">
import { onMounted, ref, watch, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProductStore } from '@/stores/product'
import ProductCard from '@/components/product/ProductCard.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import { SlidersHorizontal, ChevronLeft, ChevronRight, X } from '@lucide/vue'

const route = useRoute()
const router = useRouter()
const productStore = useProductStore()
const searchQuery = ref('')
const selectedCategory = ref('')
const sortOrder = ref('-created_at')
const currentPage = ref(1)
const minPrice = ref('')
const maxPrice = ref('')
const inStock = ref(false)
const showFilters = ref(false)
const searchError = ref(false)
const priceError = ref('')
const filterButton = ref<HTMLButtonElement | null>(null)
let fetchId = 0

const activeSearch = computed(() => typeof route.query.search === 'string' ? route.query.search : '')
const activeMin = computed(() => typeof route.query.min_price === 'string' ? route.query.min_price : '')
const activeMax = computed(() => typeof route.query.max_price === 'string' ? route.query.max_price : '')
const activeStock = computed(() => route.query.in_stock === 'true')
const selectedCategoryName = computed(() => selectedCategory.value
  ? productStore.categories.find(c => c.slug === selectedCategory.value)?.name || 'Shop'
  : 'Shop all')
const filterCount = computed(() => Number(!!selectedCategory.value) + Number(!!activeMin.value || !!activeMax.value) + Number(activeStock.value))
const priceLabel = computed(() => activeMin.value && activeMax.value ? `K${activeMin.value} – K${activeMax.value}` : activeMin.value ? `From K${activeMin.value}` : `Up to K${activeMax.value}`)
const sortOptions = [
  { value: '-created_at', label: 'Newest' },
  { value: 'price', label: 'Price: low to high' },
  { value: '-price', label: 'Price: high to low' },
  { value: '-rating', label: 'Highest rated' },
]

function syncRoute() {
  searchQuery.value = activeSearch.value
  selectedCategory.value = typeof route.query.category === 'string' ? route.query.category : ''
  sortOrder.value = typeof route.query.ordering === 'string' && sortOptions.some(o => o.value === route.query.ordering) ? route.query.ordering : '-created_at'
  const page = Number(route.query.page)
  currentPage.value = Number.isInteger(page) && page > 0 ? page : 1
  minPrice.value = activeMin.value
  maxPrice.value = activeMax.value
  inStock.value = activeStock.value
  priceError.value = ''
}

async function fetchProducts() {
  const request = ++fetchId
  searchError.value = false
  try {
    await productStore.fetchProducts({
      page: currentPage.value,
      search: activeSearch.value || undefined,
      category: selectedCategory.value || undefined,
      ordering: sortOrder.value,
      min_price: activeMin.value || undefined,
      max_price: activeMax.value || undefined,
      in_stock: activeStock.value || undefined,
    })
  } catch { if (request === fetchId) searchError.value = true }
}

function updateQuery(changes: Record<string, string | undefined>, resetPage = true) {
  const query = { ...route.query, ...changes }
  if (resetPage) delete query.page
  for (const key of Object.keys(query)) if (!query[key]) delete query[key]
  router.push({ query })
}
function handleSearch() { updateQuery({ search: searchQuery.value.trim() || undefined }) }
function selectCategory(category: string) { updateQuery({ category: category || undefined }) }
function setStock(value: boolean) { updateQuery({ in_stock: value ? 'true' : undefined }) }
function applyPrice() {
  const min = minPrice.value.trim()
  const max = maxPrice.value.trim()
  const valid = (v: string) => !v || (/^\d+(\.\d{1,2})?$/.test(v) && Number.isFinite(Number(v)))
  if (!valid(min) || !valid(max)) { priceError.value = 'Enter a valid amount with up to two decimal places.'; return }
  if (min && max && Number(min) > Number(max)) { priceError.value = 'Minimum price must be less than or equal to maximum price.'; return }
  priceError.value = ''
  updateQuery({ min_price: min || undefined, max_price: max || undefined })
}
function clearFilters() {
  minPrice.value = ''; maxPrice.value = ''; inStock.value = false; priceError.value = ''
  updateQuery({ category: undefined, min_price: undefined, max_price: undefined, in_stock: undefined })
}
function clearAll() {
  searchQuery.value = ''; minPrice.value = ''; maxPrice.value = ''; inStock.value = false; priceError.value = ''
  updateQuery({ search: undefined, category: undefined, min_price: undefined, max_price: undefined, in_stock: undefined })
}
function closeFilters() { showFilters.value = false; nextTick(() => filterButton.value?.focus()) }

onMounted(() => { productStore.fetchCategories() })
watch(() => route.query, () => { syncRoute(); fetchProducts() }, { immediate: true })
</script>

<template>
  <main class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:py-12">
    <div class="mb-7 flex flex-wrap items-end justify-between gap-4 border-b border-primary/50 pb-6">
      <div><p class="mb-2 text-xs font-semibold uppercase tracking-[.16em] text-gold">The Nzuri shop</p>
        <h1 class="font-heading text-2xl font-semibold text-dark sm:text-3xl">{{ selectedCategoryName }}</h1>
        <p class="mt-2 text-sm text-muted" aria-live="polite">{{ productStore.loading ? 'Finding products…' : searchError ? 'Products unavailable' : `${productStore.pagination.count} ${productStore.pagination.count === 1 ? 'product' : 'products'}` }}</p>
      </div>
      <div class="flex w-full items-center gap-3 sm:w-auto">
        <button ref="filterButton" type="button" class="flex min-h-11 flex-1 items-center justify-center gap-2 rounded-xl border border-[#b9a8a8] bg-white px-4 text-sm font-semibold text-dark hover:bg-primary/20 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold md:hidden" :aria-expanded="showFilters" aria-controls="catalog-filters" @click="showFilters = !showFilters">
          <SlidersHorizontal class="h-4 w-4" /> Filters <span v-if="filterCount" class="grid h-5 min-w-5 place-items-center rounded-full bg-dark px-1 text-xs text-white">{{ filterCount }}</span>
        </button>
        <div class="flex flex-1 items-center gap-2 sm:flex-none"><label for="catalog-sort" class="whitespace-nowrap text-sm text-muted">Sort by</label>
          <select id="catalog-sort" :value="sortOrder" class="min-h-11 min-w-0 flex-1 rounded-xl border border-[#b9a8a8] bg-white px-3 text-sm text-dark focus-visible:outline-2 focus-visible:outline-gold sm:w-44" @change="updateQuery({ ordering: ($event.target as HTMLSelectElement).value === '-created_at' ? undefined : ($event.target as HTMLSelectElement).value })">
            <option v-for="option in sortOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
          </select>
        </div>
      </div>
    </div>

    <form class="mb-6 flex gap-2" role="search" @submit.prevent="handleSearch">
      <label for="catalog-search" class="sr-only">Search products</label>
      <input id="catalog-search" v-model="searchQuery" type="search" placeholder="Search products..." class="min-h-11 min-w-0 flex-1 rounded-xl border border-[#b9a8a8] bg-white px-4 text-base text-dark focus:outline-none focus:ring-2 focus:ring-gold/40" />
      <BaseButton type="submit" variant="secondary">Search</BaseButton>
    </form>

    <div v-if="filterCount || activeSearch" class="mb-6 flex flex-wrap items-center gap-2" aria-label="Active filters">
      <span class="mr-1 text-sm font-medium text-muted">Active:</span>
      <button v-if="activeSearch" type="button" class="filter-chip" :aria-label="`Remove search ${activeSearch}`" @click="updateQuery({ search: undefined })">Search: {{ activeSearch }} <X class="h-4 w-4" /></button>
      <button v-if="selectedCategory" type="button" class="filter-chip" :aria-label="`Remove ${selectedCategoryName} filter`" @click="selectCategory('')">{{ selectedCategoryName }} <X class="h-4 w-4" /></button>
      <button v-if="activeMin || activeMax" type="button" class="filter-chip" aria-label="Remove price filter" @click="updateQuery({ min_price: undefined, max_price: undefined })">{{ priceLabel }} <X class="h-4 w-4" /></button>
      <button v-if="activeStock" type="button" class="filter-chip" aria-label="Remove in stock filter" @click="setStock(false)">In stock <X class="h-4 w-4" /></button>
      <button v-if="filterCount" type="button" class="min-h-11 px-2 text-sm font-medium text-gold underline underline-offset-4" @click="clearFilters">Clear filters</button>
    </div>

    <div class="flex flex-col gap-8 md:flex-row">
      <aside id="catalog-filters" class="filter-panel w-full shrink-0 rounded-2xl border border-primary/50 bg-white p-5 md:block md:w-60 md:self-start" :class="showFilters ? 'block' : 'hidden'" aria-label="Product filters">
        <div class="filter-heading mb-5 flex items-center justify-between"><h2 class="font-heading text-base font-semibold text-dark">Filters</h2><button v-if="filterCount" type="button" class="text-sm text-gold underline underline-offset-4" @click="clearFilters">Clear all</button></div>
        <fieldset class="filter-group border-t border-primary/50 py-5"><legend class="sr-only">Category</legend><p aria-hidden="true" class="filter-group-title mb-3 text-sm font-semibold text-dark">Category</p>
          <label class="filter-option"><input type="radio" name="category" :checked="!selectedCategory" @change="selectCategory('')" /><span>All products</span></label>
          <label v-for="cat in productStore.categories" :key="cat.id" class="filter-option"><input type="radio" name="category" :checked="selectedCategory === cat.slug" @change="selectCategory(cat.slug)" /><span class="min-w-0 flex-1">{{ cat.name }}</span><span class="text-xs text-muted">{{ cat.product_count ?? 0 }}</span></label>
        </fieldset>
        <fieldset class="filter-group border-t border-primary/50 py-5"><legend class="sr-only">Price in Zambian kwacha</legend><p aria-hidden="true" class="mb-1 text-sm font-semibold text-dark">Price</p><p class="price-hint mb-3 text-xs text-muted">Set a range in ZMW</p>
          <div class="grid grid-cols-2 gap-2"><label class="price-label">Min (K)<input v-model="minPrice" type="text" inputmode="decimal" placeholder="0" :aria-invalid="!!priceError" :aria-describedby="priceError ? 'price-error' : undefined" /></label><label class="price-label">Max (K)<input v-model="maxPrice" type="text" inputmode="decimal" placeholder="Any" :aria-invalid="!!priceError" :aria-describedby="priceError ? 'price-error' : undefined" /></label></div>
          <p v-if="priceError" id="price-error" role="alert" class="mt-2 text-sm text-red-700">{{ priceError }}</p>
          <button type="button" class="price-apply mt-3 min-h-10 w-full rounded-xl border border-[#b9a8a8] text-sm font-semibold text-dark hover:bg-primary/20 focus-visible:outline-2 focus-visible:outline-gold" @click="applyPrice">Apply price</button>
        </fieldset>
        <fieldset class="filter-group filter-availability border-t border-primary/50 pt-5"><legend class="sr-only">Availability</legend><p aria-hidden="true" class="filter-group-title mb-3 text-sm font-semibold text-dark">Availability</p><label class="filter-option"><input type="checkbox" :checked="activeStock" @change="setStock(($event.target as HTMLInputElement).checked)" /><span>In stock only</span></label></fieldset>
        <button type="button" class="mt-5 min-h-11 w-full rounded-xl bg-dark text-sm font-semibold text-white md:hidden" @click="closeFilters">Show products</button>
      </aside>
      <section class="min-w-0 flex-1" aria-label="Products" :aria-busy="productStore.loading">
        <div v-if="productStore.loading" class="grid grid-cols-2 gap-4 md:grid-cols-3 md:gap-6" role="status"><span class="sr-only">Loading products</span><div v-for="i in 6" :key="i" class="space-y-3"><div class="aspect-[3/4] animate-pulse rounded-[20px] bg-primary/30" /><div class="h-4 w-28 rounded bg-primary/30" /></div></div>
        <div v-else-if="searchError" class="py-16 text-center" role="alert"><p class="mb-2 font-medium text-dark">Products could not be loaded.</p><button class="text-sm underline" @click="fetchProducts">Try again</button></div>
        <div v-else-if="!productStore.products.length" class="rounded-2xl border border-primary/40 bg-white px-5 py-16 text-center"><p class="font-medium text-dark">No products found</p><p class="mt-2 text-sm text-muted">Try a different search or remove a filter.</p><BaseButton variant="outline" class="mt-5" @click="clearAll">Clear search &amp; filters</BaseButton></div>
        <div v-else class="grid grid-cols-2 gap-4 md:grid-cols-3 md:gap-6"><ProductCard v-for="product in productStore.products" :key="product.id" :product="product" /></div>
        <nav v-if="!productStore.loading && productStore.pagination.count > 12" class="mt-10 flex items-center justify-center gap-4" aria-label="Product pages"><button :disabled="!productStore.pagination.previous" class="page-button" @click="updateQuery({ page: currentPage - 1 > 1 ? String(currentPage - 1) : undefined }, false)"><ChevronLeft class="h-4 w-4" /> Previous</button><span class="text-sm text-muted">Page {{ currentPage }} of {{ Math.ceil(productStore.pagination.count / 12) }}</span><button :disabled="!productStore.pagination.next" class="page-button" @click="updateQuery({ page: String(currentPage + 1) }, false)">Next <ChevronRight class="h-4 w-4" /></button></nav>
      </section>
    </div>
  </main>
</template>

<style scoped>
.filter-option { display:flex; align-items:center; gap:.625rem; min-height:2.75rem; font-size:.875rem; color:var(--color-dark); cursor:pointer; }
.filter-option input { width:1.05rem; height:1.05rem; accent-color:var(--color-gold); flex:none; }
.filter-option input:focus-visible { outline:2px solid var(--color-gold); outline-offset:3px; }
.price-label { display:grid; gap:.375rem; font-size:.75rem; font-weight:600; color:var(--color-muted); }
.price-label input { width:100%; min-width:0; min-height:2.75rem; border:1px solid #b9a8a8; border-radius:.75rem; padding:0 .625rem; color:var(--color-dark); background:white; font-size:1rem; }
.price-label input:focus-visible { outline:2px solid var(--color-gold); outline-offset:1px; }
.filter-chip { display:inline-flex; align-items:center; gap:.375rem; min-height:2.75rem; border-radius:999px; background:#f2e4e6; padding:.4rem .75rem; font-size:.875rem; color:#51383c; }
.filter-chip:focus-visible,.page-button:focus-visible { outline:2px solid var(--color-gold); outline-offset:2px; }
.page-button { display:flex; align-items:center; gap:.25rem; min-height:2.75rem; border:1px solid #b9a8a8; border-radius:.75rem; padding:.5rem .75rem; font-size:.875rem; }
.page-button:disabled { opacity:.4; cursor:not-allowed; }
@media (min-width: 768px) {
  .filter-panel { position:sticky; top:5.5rem; max-height:calc(100dvh - 6.5rem); overflow-y:auto; overscroll-behavior:contain; padding:1rem; scrollbar-width:thin; }
  .filter-heading { margin-bottom:.75rem; }
  .filter-group { padding-top:.75rem; padding-bottom:.75rem; }
  .filter-availability { padding-bottom:0; }
  .filter-group-title { margin-bottom:.375rem; }
  .price-hint { margin-bottom:.5rem; }
  .price-apply { margin-top:.5rem; }
}
@media (min-width: 768px) and (pointer:fine) {
  .filter-option { min-height:2rem; }
}
</style>
