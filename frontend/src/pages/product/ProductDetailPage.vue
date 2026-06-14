<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useProductStore } from '@/stores/product'
import { useCartStore } from '@/stores/cart'
import { useWishlistStore } from '@/stores/wishlist'
import ProductGallery from '@/components/product/ProductGallery.vue'
import ProductCard from '@/components/product/ProductCard.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import { Heart, Minus, Plus, Star, Truck, ShieldCheck } from '@lucide/vue'
import type { Product } from '@/types'

const route = useRoute()
const productStore = useProductStore()
const cartStore = useCartStore()
const wishlistStore = useWishlistStore()

const quantity = ref(1)
const addedToCart = ref(false)
const recentlyViewed = ref<Product[]>([])

const product = computed(() => productStore.currentProduct)
const inStock = computed(() => product.value?.is_in_stock ?? false)
const inWishlist = computed(() => product.value ? wishlistStore.isWishlisted(product.value.id) : false)
const stockLabel = computed(() => {
  if (!product.value) return ''
  if (product.value.stock === 0) return 'Out of Stock'
  if (product.value.stock <= 5) return `Only ${product.value.stock} left`
  return 'In Stock'
})

const ratingStars = computed(() => {
  if (!product.value) return []
  return Array.from({ length: 5 }, (_, i) => i < Math.round(product.value!.rating))
})

function incrementQty() {
  if (product.value && quantity.value < product.value.stock) {
    quantity.value++
  }
}

function decrementQty() {
  if (quantity.value > 1) quantity.value--
}

function handleAddToCart() {
  if (product.value) {
    cartStore.addToCart(product.value, quantity.value)
    addedToCart.value = true
    setTimeout(() => { addedToCart.value = false }, 2000)
  }
}

function handleToggleWishlist() {
  if (product.value) {
    wishlistStore.toggle(product.value)
  }
}

function trackRecentlyViewed(p: Product) {
  const key = 'bynzuri_recently_viewed'
  const stored = localStorage.getItem(key)
  let items: Product[] = stored ? JSON.parse(stored) : []
  items = items.filter(i => i.id !== p.id)
  items.unshift(p)
  if (items.length > 6) items = items.slice(0, 6)
  localStorage.setItem(key, JSON.stringify(items))
  recentlyViewed.value = items
}

function loadRecentlyViewed() {
  const key = 'bynzuri_recently_viewed'
  const stored = localStorage.getItem(key)
  if (stored) {
    recentlyViewed.value = JSON.parse(stored).slice(0, 4)
  }
}

onMounted(() => {
  const slug = route.params.slug as string
  productStore.fetchProduct(slug)
  loadRecentlyViewed()
})

watch(product, (p) => {
  if (p) {
    trackRecentlyViewed(p)
  }
  if (p?.category) {
    productStore.fetchRelatedProducts(p.category)
  }
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 py-8">
    <template v-if="productStore.loading && !product">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div class="aspect-[3/4] rounded-[20px] bg-primary/30 animate-pulse" />
        <div class="space-y-4">
          <div class="h-4 w-20 bg-primary/30 rounded animate-pulse" />
          <div class="h-8 w-64 bg-primary/30 rounded animate-pulse" />
          <div class="h-6 w-24 bg-primary/30 rounded animate-pulse" />
          <div class="h-20 w-full bg-primary/30 rounded animate-pulse" />
        </div>
      </div>
    </template>

    <template v-else-if="product">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-10">
        <ProductGallery :images="product.images" />

        <div class="md:sticky md:top-24 md:self-start">
          <p class="text-xs text-gold uppercase tracking-[0.2em] font-medium mb-2">
            {{ product.category_name }}
          </p>

          <h1 class="font-heading text-2xl md:text-3xl font-semibold text-dark mb-3">
            {{ product.title }}
          </h1>

          <p class="font-bold text-2xl text-dark mb-4">K{{ product.price }}</p>

          <div class="flex items-center gap-2 mb-4">
            <div class="flex items-center gap-0.5">
              <Star
                v-for="(filled, i) in ratingStars"
                :key="i"
                class="w-4 h-4"
                :class="filled ? 'text-gold fill-gold' : 'text-muted/30'"
              />
            </div>
            <span v-if="product.review_count > 0" class="text-xs text-muted">
              ({{ product.review_count }} reviews)
            </span>
          </div>

          <div class="flex items-center gap-2 mb-6">
            <span
              class="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full"
              :class="inStock ? 'bg-success/10 text-success' : 'bg-red-50 text-red-500'"
            >
              <span class="w-1.5 h-1.5 rounded-full" :class="inStock ? 'bg-success' : 'bg-red-500'" />
              {{ stockLabel }}
            </span>
          </div>

          <p class="text-sm text-muted leading-relaxed mb-6">
            {{ product.description }}
          </p>

          <div v-if="inStock" class="flex items-center gap-3 mb-6">
            <div class="flex items-center border border-primary/40 rounded-[14px] overflow-hidden">
              <button
                class="p-3 hover:bg-primary/30 transition-colors"
                @click="decrementQty"
                :disabled="quantity <= 1"
              >
                <Minus class="w-4 h-4" />
              </button>
              <span class="px-4 text-sm font-medium min-w-[40px] text-center">{{ quantity }}</span>
              <button
                class="p-3 hover:bg-primary/30 transition-colors"
                @click="incrementQty"
                :disabled="quantity >= product.stock"
              >
                <Plus class="w-4 h-4" />
              </button>
            </div>

            <BaseButton
              variant="secondary"
              :fullWidth="true"
              @click="handleAddToCart"
            >
              <template v-if="addedToCart">Added!</template>
              <template v-else>Add to Cart</template>
            </BaseButton>
          </div>

          <div class="flex items-center gap-2 text-xs text-muted py-4 border-t border-primary/20">
            <button
              class="flex items-center gap-1.5 hover:text-dark transition-colors active:scale-95"
              @click="handleToggleWishlist"
            >
              <Heart
                class="w-3.5 h-3.5 transition-all"
                :class="inWishlist ? 'text-red-500 fill-red-500' : ''"
              />
              {{ inWishlist ? 'Remove from Wishlist' : 'Add to Wishlist' }}
            </button>
          </div>

          <div class="space-y-3 pt-4 border-t border-primary/20">
            <div class="flex items-start gap-3">
              <Truck class="w-4 h-4 text-gold mt-0.5 shrink-0" />
              <div>
                <p class="text-sm font-medium text-dark">Nationwide Delivery</p>
                <p class="text-xs text-muted">Fast and reliable delivery across all Zambian provinces</p>
              </div>
            </div>
            <div class="flex items-start gap-3">
              <ShieldCheck class="w-4 h-4 text-gold mt-0.5 shrink-0" />
              <div>
                <p class="text-sm font-medium text-dark">Secure Payments</p>
                <p class="text-xs text-muted">MTN MoMo, Airtel Money, Visa &amp; Mastercard accepted</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Reviews Section -->
      <section class="mt-16 pt-8 border-t border-primary/20">
        <h2 class="font-heading text-xl font-semibold text-dark mb-6">Customer Reviews</h2>
        <div class="text-center py-8 text-muted text-sm">
          <p>Reviews coming soon. Be the first to review this product.</p>
        </div>
      </section>

      <!-- Related Products -->
      <section class="mt-16">
        <h2 class="font-heading text-xl font-semibold text-dark mb-6">You May Also Like</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
          <ProductCard
            v-for="p in productStore.relatedProducts"
            :key="p.id"
            :product="p"
          />
        </div>
      </section>

      <!-- Recently Viewed -->
      <section v-if="recentlyViewed.length > 0" class="mt-16 mb-8">
        <h2 class="font-heading text-xl font-semibold text-dark mb-6">Recently Viewed</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
          <ProductCard
            v-for="p in recentlyViewed"
            :key="p.id"
            :product="p"
          />
        </div>
      </section>
    </template>
  </div>
</template>
