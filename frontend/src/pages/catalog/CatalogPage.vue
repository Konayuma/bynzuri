<script setup lang="ts">
import { onMounted, ref, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProductStore } from '@/stores/product'
import ProductCard from '@/components/product/ProductCard.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import { Search, SlidersHorizontal, ChevronLeft, ChevronRight, X } from '@lucide/vue'

const route = useRoute()
const router = useRouter()
const productStore = useProductStore()

const searchQuery = ref((route.query.search as string) || '')
const selectedCategory = ref((route.query.category as string) || '')
const sortOrder = ref((route.query.ordering as string) || '-created_at')
const currentPage = ref(Number(route.query.page) || 1)
const showFilters = ref(false)
const searchError = ref(false)

const activeSearch = computed(() => (route.query.search as string) || '')

const selectedCategoryName = computed(() => {
  if (!selectedCategory.value) return 'Shop All'
  return productStore.categories.find(c => c.slug === selectedCategory.value)?.name || 'Shop'
})

const sortOptions = [
  { value: '-created_at', label: 'Newest' },
  { value: 'price', label: 'Price: Low to High' },
  { value: '-price', label: 'Price: High to Low' },
  { value: '-rating', label: 'Highest Rated' }
]

async function fetchProducts() {
  searchError.value = false
  try {
  await productStore.fetchProducts({
    page: currentPage.value,
    search: searchQuery.value || undefined,
    category: selectedCategory.value || undefined,
    ordering: sortOrder.value
  })
  } catch { searchError.value = true }
}

function handleSearch() {
  currentPage.value = 1
  updateUrl()
}

function clearSearch() {
  searchQuery.value = ''
  selectedCategory.value = ''
  currentPage.value = 1
  updateUrl()
}

function handleCategoryChange(category: string) {
  selectedCategory.value = category
  currentPage.value = 1
  updateUrl()
}

function handleSortChange() {
  currentPage.value = 1
  updateUrl()
}

function changePage(delta: number) {
  currentPage.value += delta
  updateUrl()
}

function updateUrl() {
  const query: Record<string, string> = {}
  if (searchQuery.value) query.search = searchQuery.value
  if (selectedCategory.value) query.category = selectedCategory.value
  if (sortOrder.value !== '-created_at') query.ordering = sortOrder.value
  if (currentPage.value > 1) query.page = String(currentPage.value)
  router.replace({ query })
}

onMounted(() => {
  productStore.fetchCategories()
  fetchProducts()
})

watch(() => route.query, () => {
  searchQuery.value = (route.query.search as string) || ''
  selectedCategory.value = (route.query.category as string) || ''
  sortOrder.value = (route.query.ordering as string) || '-created_at'
  currentPage.value = Number(route.query.page) || 1
  fetchProducts()
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 py-8">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
      <div>
        <h1 class="font-heading text-2xl md:text-3xl font-semibold text-dark">
          {{ selectedCategoryName }}
        </h1>
        <div class="flex items-center gap-2 mt-1">
          <p v-if="productStore.pagination.count > 0" class="text-sm text-muted">
            {{ productStore.pagination.count }} products
          </p>
          <span v-if="activeSearch" class="inline-flex items-center gap-1.5 text-sm text-gold bg-gold/10 px-2.5 py-0.5 rounded-full">
            <Search class="w-3 h-3" />
            "{{ activeSearch }}"
            <button class="hover:text-dark transition-colors" aria-label="Clear search and filters" @click="clearSearch">
              <X class="w-3 h-3" />
            </button>
          </span>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <button
          aria-label="Toggle filters" :aria-expanded="showFilters"
          class="md:hidden p-2.5 border border-primary/40 rounded-[14px] hover:bg-primary/20 transition-colors"
          @click="showFilters = !showFilters"
        >
          <SlidersHorizontal class="w-4 h-4" />
        </button>

        <select
          v-model="sortOrder"
          class="px-3 py-2.5 bg-white border border-primary/40 rounded-[14px] text-sm focus:outline-none focus:border-gold transition-colors"
          @change="handleSortChange"
        >
          <option v-for="opt in sortOptions" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
      </div>
    </div>

    <div class="flex flex-col md:flex-row gap-8">
      <aside
        class="shrink-0 w-full md:w-56 space-y-6"
        :class="showFilters ? 'block' : 'hidden md:block'"
      >
        <div>
          <h3 class="text-sm font-semibold text-dark mb-3">Categories</h3>
          <div class="space-y-1.5">
            <button
              class="block w-full text-left px-3 py-2 text-sm rounded-lg transition-colors"
              :class="!selectedCategory ? 'bg-primary/50 text-dark font-medium' : 'text-muted hover:text-dark hover:bg-primary/20'"
              @click="handleCategoryChange('')"
            >
              All Products
            </button>
            <button
              v-for="cat in productStore.categories"
              :key="cat.id"
              class="block w-full text-left px-3 py-2 text-sm rounded-lg transition-colors"
              :class="selectedCategory === cat.slug ? 'bg-primary/50 text-dark font-medium' : 'text-muted hover:text-dark hover:bg-primary/20'"
              @click="handleCategoryChange(cat.slug)"
            >
              {{ cat.name }}
              <span v-if="cat.product_count" class="text-xs text-muted ml-1">({{ cat.product_count }})</span>
            </button>
          </div>
        </div>

        <div class="md:hidden">
          <select
            v-model="sortOrder"
            class="w-full px-3 py-2.5 bg-white border border-primary/40 rounded-[14px] text-sm focus:outline-none focus:border-gold transition-colors"
            @change="handleSortChange"
          >
            <option v-for="opt in sortOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
        </div>
      </aside>

      <div class="flex-1">
        <div
          v-if="productStore.loading"
          class="grid grid-cols-2 md:grid-cols-3 gap-4 md:gap-6"
        >
          <div v-for="i in 6" :key="i" class="space-y-3">
            <div class="aspect-[3/4] rounded-[20px] bg-primary/30 animate-pulse" />
            <div class="h-3 w-16 bg-primary/30 rounded animate-pulse" />
            <div class="h-4 w-28 bg-primary/30 rounded animate-pulse" />
            <div class="h-4 w-16 bg-primary/30 rounded animate-pulse" />
          </div>
        </div>

        <div v-else-if="searchError" class="text-center py-16" role="alert"><p class="text-dark font-medium mb-2">Products could not be loaded.</p><button class="underline text-sm" @click="fetchProducts">Try again</button></div>

        <div
          v-else-if="productStore.products.length === 0"
          class="text-center py-16"
        >
          <p class="text-dark font-medium mb-1">No products found</p>
          <p class="text-sm text-muted mb-4">Try adjusting your search or filters.</p>
          <BaseButton variant="outline" class="mt-4" @click="clearSearch">
            Clear Search &amp; Filters
          </BaseButton>
        </div>

        <div
          v-else
          class="grid grid-cols-2 md:grid-cols-3 gap-4 md:gap-6"
        >
          <ProductCard
            v-for="product in productStore.products"
            :key="product.id"
            :product="product"
          />
        </div>

        <!-- Pagination -->
        <div
          v-if="productStore.pagination.count > 12"
          class="flex items-center justify-center gap-4 mt-10"
        >
          <button
            :disabled="!productStore.pagination.previous"
            class="flex items-center gap-1 px-4 py-2 text-sm rounded-[14px] border border-primary/40 hover:bg-primary/20 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            @click="changePage(-1)"
          >
            <ChevronLeft class="w-4 h-4" /> Previous
          </button>
          <span class="text-sm text-muted">
            Page {{ currentPage }} of {{ Math.ceil(productStore.pagination.count / 12) }}
          </span>
          <button
            :disabled="!productStore.pagination.next"
            class="flex items-center gap-1 px-4 py-2 text-sm rounded-[14px] border border-primary/40 hover:bg-primary/20 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            @click="changePage(1)"
          >
            Next <ChevronRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
