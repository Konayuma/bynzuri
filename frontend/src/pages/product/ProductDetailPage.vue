<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useProductStore } from '@/stores/product'
import { useCartStore } from '@/stores/cart'
import { useWishlistStore } from '@/stores/wishlist'
import { useUserStore } from '@/stores/user'
import ProductGallery from '@/components/product/ProductGallery.vue'
import ProductCard from '@/components/product/ProductCard.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import { Heart, Minus, Plus, Star, Truck, ShieldCheck, Send } from '@lucide/vue'
import type { Product } from '@/types'

const route = useRoute()
const productStore = useProductStore()
const cartStore = useCartStore()
const wishlistStore = useWishlistStore()
const userStore = useUserStore()

const quantity = ref(1)
const addedToCart = ref(false)
const recentlyViewed = ref<Product[]>([])

const reviewRating = ref(5)
const reviewComment = ref('')
const reviewSubmitting = ref(false)
const reviewError = ref('')
const reviewSuccess = ref(false)

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

async function submitReview() {
  if (!reviewComment.value.trim()) {
    reviewError.value = 'Write a few words about your experience'
    return
  }
  reviewSubmitting.value = true
  reviewError.value = ''
  reviewSuccess.value = false
  try {
    await productStore.createReview({
      product_slug: route.params.slug as string,
      rating: reviewRating.value,
      comment: reviewComment.value.trim(),
    })
    reviewSuccess.value = true
    reviewComment.value = ''
    reviewRating.value = 5
    if (product.value) {
      product.value.review_count++
    }
  } catch (e: any) {
    reviewError.value = e.response?.data?.detail || 'Could not submit your review. Please try again.'
  } finally {
    reviewSubmitting.value = false
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-ZM', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

onMounted(() => {
  const slug = route.params.slug as string
  productStore.fetchProduct(slug)
  productStore.fetchReviews(slug)
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
              <template v-if="addedToCart">Added to Cart!</template>
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

        <!-- Review Form -->
        <div v-if="userStore.isAuthenticated" class="bg-white rounded-[16px] p-5 border border-primary/20 mb-6">
          <h3 class="text-sm font-medium text-dark mb-3">Write a Review</h3>
          <div class="flex items-center gap-1 mb-3">
            <button
              v-for="i in 5"
              :key="i"
              type="button"
              class="p-0.5"
              @click="reviewRating = i"
            >
              <Star
                class="w-5 h-5 transition-colors"
                :class="i <= reviewRating ? 'text-gold fill-gold' : 'text-muted/30'"
              />
            </button>
          </div>
          <textarea
            v-model="reviewComment"
            class="w-full px-4 py-3 bg-white border border-primary/40 rounded-[14px] text-sm text-dark placeholder:text-muted/60 focus:outline-none focus:border-gold transition-colors"
            rows="3"
            placeholder="Share your experience with this product..."
          />
          <div class="flex items-center justify-between mt-3">
            <p v-if="reviewError" class="text-xs text-red-500">{{ reviewError }}</p>
            <p v-if="reviewSuccess" class="text-xs text-success">Thanks! Your review has been submitted.</p>
            <div />
            <BaseButton size="sm" :loading="reviewSubmitting" @click="submitReview">
              <Send class="w-3.5 h-3.5 mr-1.5" /> Submit
            </BaseButton>
          </div>
        </div>
        <div v-else class="text-center py-4 mb-6 bg-primary/10 rounded-[14px]">
          <p class="text-sm text-muted">
            <router-link to="/auth/login" class="text-gold hover:underline">Sign in</router-link> to write a review
          </p>
        </div>

        <!-- Reviews List -->
        <div v-if="productStore.reviews.length > 0" class="space-y-4">
          <div
            v-for="review in productStore.reviews"
            :key="review.id"
            class="bg-white rounded-[14px] p-4 border border-primary/10"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2">
                <div class="w-8 h-8 rounded-full bg-primary/30 flex items-center justify-center">
                  <span class="text-xs font-medium text-dark">{{ review.user_name?.charAt(0) || 'U' }}</span>
                </div>
                <span class="text-sm font-medium text-dark">{{ review.user_name || 'Anonymous' }}</span>
              </div>
              <span class="text-xs text-muted">{{ formatDate(review.created_at) }}</span>
            </div>
            <div class="flex items-center gap-0.5 mb-2">
              <Star
                v-for="i in 5"
                :key="i"
                class="w-3.5 h-3.5"
                :class="i <= review.rating ? 'text-gold fill-gold' : 'text-muted/30'"
              />
            </div>
            <p class="text-sm text-muted leading-relaxed">{{ review.comment }}</p>
          </div>
        </div>
        <div v-else class="text-center py-8 text-muted text-sm">
          No reviews yet. Share your experience to help others.
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
