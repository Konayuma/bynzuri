<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useProductStore } from '@/stores/product'
import { useCartStore } from '@/stores/cart'
import { useWishlistStore } from '@/stores/wishlist'
import { useUserStore } from '@/stores/user'
import { useUIStore } from '@/stores/ui'
import ProductGallery from '@/components/product/ProductGallery.vue'
import DescriptionInline from '@/components/product/DescriptionInline.vue'
import ProductCard from '@/components/product/ProductCard.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import { Heart, Minus, Plus, Star, Truck, ShieldCheck, Send, ChevronRight } from '@lucide/vue'
import type { Product, Review } from '@/types'
import { reviewService } from '@/services/review.service'
import { signatureImage } from '@/utils/productImage'
import { formatProductDescription } from '@/utils/productDescription'
import { isValidReviewComment } from '@/utils/formValidation'

const route = useRoute()
const productStore = useProductStore()
const cartStore = useCartStore()
const wishlistStore = useWishlistStore()
const userStore = useUserStore()
const uiStore = useUIStore()

const quantity = ref(1)
const addedToCart = ref(false)
const addingToCart = ref(false)
const cartError = ref('')
const recentlyViewed = ref<Product[]>([])
const productError = ref(false)

const reviewRating = ref(5)
const reviewComment = ref('')
const reviewSubmitting = ref(false)
const reviewError = ref('')
const ownReview = ref<Review | null>(null)
const editingReview = ref(false)
const ownReviewError = ref(false)
const ownReviewLoading = ref(false)
let ownRequest = 0
async function loadOwnReview() {
  const request = ++ownRequest
  ownReview.value = null
  ownReviewError.value = false
  const slug = route.params.slug
  if (!userStore.isAuthenticated || typeof slug !== 'string') { ownReviewLoading.value = false; return }
  ownReviewLoading.value = true
  try {
    const result = await reviewService.getMine(slug)
    if (request === ownRequest) ownReview.value = result
  } catch {
    if (request === ownRequest) ownReviewError.value = true
  } finally {
    if (request === ownRequest) ownReviewLoading.value = false
  }
}
function startEditing() {
  if (!ownReview.value) return
  reviewRating.value = ownReview.value.rating
  reviewComment.value = ownReview.value.comment
  reviewError.value = ''
  editingReview.value = true
}
async function deleteOwnReview() {
  if (!ownReview.value || reviewSubmitting.value || !window.confirm('Delete your review?')) return
  reviewSubmitting.value = true
  try {
    await reviewService.deleteReview(ownReview.value.id)
    ownReview.value = null
    editingReview.value = false
    await productStore.fetchReviews(String(route.params.slug))
    await productStore.fetchProduct(String(route.params.slug)).catch(() => {})
  } catch { reviewError.value = 'Could not delete your review. Please try again.' }
  finally { reviewSubmitting.value = false }
}

const product = computed(() => productStore.currentProduct)
const descriptionBlocks = computed(() => formatProductDescription(product.value?.description || ''))
const galleryImages = computed(() => {
  if (!product.value) return []
  if (product.value.images?.length) return product.value.images
  const image = signatureImage(product.value.slug)
  return image ? [{ id: product.value.slug, image, alt_text: product.value.title, is_primary: true }] : []
})
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

const filteredRelatedProducts = computed(() =>
  productStore.relatedProducts.filter(p => p.id !== product.value?.id).slice(0, 4)
)

const filteredRecentlyViewed = computed(() =>
  recentlyViewed.value.filter(p => p.id !== product.value?.id).slice(0, 4)
)

function incrementQty() {
  if (product.value && quantity.value < product.value.stock) {
    quantity.value++
  }
}

function decrementQty() {
  if (quantity.value > 1) quantity.value--
}

async function handleAddToCart() {
  if (!product.value || addingToCart.value) return
  addingToCart.value = true
  cartError.value = ''
  try {
    await cartStore.addToCart(product.value, quantity.value)
    addedToCart.value = true
    uiStore.showToast(`Added ${product.value.title} to your bag`, {
      actionLabel: 'View bag',
      onAction: () => uiStore.openCart(),
    })
    setTimeout(() => { addedToCart.value = false }, 2000)
  } catch {
    cartError.value = cartStore.error || 'Could not add this product. Please try again.'
  } finally {
    addingToCart.value = false
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
  const trimmed = reviewComment.value.trim()
  if (reviewRating.value < 1 || reviewRating.value > 5) {
    reviewError.value = 'Select a rating between 1 and 5 stars.'
    return
  }
  if (!trimmed) {
    reviewError.value = 'Write a few words about your experience.'
    return
  }
  if (!isValidReviewComment(trimmed)) {
    reviewError.value = trimmed.length < 5
      ? 'Please write at least 5 characters so your review is helpful to other shoppers.'
      : 'Keep your review under 1,000 characters.'
    return
  }
  reviewSubmitting.value = true
  reviewError.value = ''
  try {
    const data = { rating: reviewRating.value, comment: trimmed }
    ownReview.value = editingReview.value && ownReview.value
      ? await reviewService.updateReview(ownReview.value.id, data)
      : await productStore.createReview({ product_slug: route.params.slug as string, ...data })
    editingReview.value = false
    await productStore.fetchReviews(String(route.params.slug))
    await productStore.fetchProduct(String(route.params.slug)).catch(() => {})
    uiStore.showToast('Thank you! Your review was submitted for approval.', { duration: 5000 })
    reviewComment.value = ''
    reviewRating.value = 5
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

onMounted(loadRecentlyViewed)

watch(() => route.params.slug, async (slug) => {
  if (typeof slug !== 'string' || !slug) return
  productError.value = false
  quantity.value = 1
  addedToCart.value = false
  reviewComment.value = ''
  reviewRating.value = 5
  reviewError.value = ''
  productStore.fetchReviews(slug)
  try {
    await productStore.fetchProduct(slug)
  } catch {
    if (route.params.slug === slug) productError.value = true
  }
}, { immediate: true })

watch(() => [route.params.slug, userStore.user?.id], () => { editingReview.value = false; void loadOwnReview() }, { immediate: true })

watch(product, (p) => {
  if (p) {
    trackRecentlyViewed(p)
  }
  if (p?.category_slug) {
    productStore.fetchRelatedProducts(p.category_slug)
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

    <div v-else-if="productError" role="alert" class="mx-auto max-w-md py-20 text-center">
      <h1 class="font-heading text-xl font-semibold text-dark">Product unavailable</h1>
      <p class="mt-2 text-sm text-muted">We couldn’t load this product. Please try again or browse the collection.</p>
      <router-link to="/catalog" class="mt-5 inline-block rounded-xl bg-dark px-5 py-3 text-sm font-medium text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold">Browse products</router-link>
    </div>
    <template v-else-if="product">
      <nav aria-label="Breadcrumb" class="mb-5 flex flex-wrap items-center gap-1.5 text-xs text-muted">
        <router-link to="/" class="hover:text-dark transition-colors">Home</router-link>
        <ChevronRight class="w-3.5 h-3.5 shrink-0" aria-hidden="true" />
        <router-link to="/catalog" class="hover:text-dark transition-colors">Shop</router-link>
        <template v-if="product.category_slug">
          <ChevronRight class="w-3.5 h-3.5 shrink-0" aria-hidden="true" />
          <router-link :to="{ path: '/catalog', query: { category: product.category_slug } }" class="hover:text-dark transition-colors">
            {{ product.category_name }}
          </router-link>
        </template>
        <ChevronRight class="w-3.5 h-3.5 shrink-0" aria-hidden="true" />
        <span class="text-dark font-medium truncate max-w-[200px] sm:max-w-xs" aria-current="page">{{ product.title }}</span>
      </nav>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-10">
        <ProductGallery :key="product.slug" :images="galleryImages" />

        <div class="md:sticky md:top-24 md:self-start">
          <router-link
            v-if="product.category_slug"
            :to="{ path: '/catalog', query: { category: product.category_slug } }"
            class="inline-block text-xs text-gold uppercase tracking-[0.2em] font-medium mb-2 hover:underline"
          >
            {{ product.category_name }}
          </router-link>
          <p v-else class="text-xs text-gold uppercase tracking-[0.2em] font-medium mb-2">
            {{ product.category_name }}
          </p>

          <h1 class="font-heading text-2xl md:text-3xl font-semibold text-dark mb-3">
            {{ product.title }}
          </h1>

          <p class="font-bold text-2xl text-dark mb-4 tabular-nums"><span v-if="Number(product.effective_discount_percent ?? product.discount_percent) > 0" class="mr-3 text-base font-normal text-muted line-through">K{{ product.price }}</span>K{{ product.sale_price ?? product.price }}</p>

          <div class="flex items-center gap-2 mb-4">
            <template v-if="product.review_count > 0">
              <a href="#reviews" class="inline-flex items-center gap-2 hover:opacity-80 transition-opacity">
                <div class="flex items-center gap-0.5" :aria-label="`Rated ${Number(product.rating).toFixed(1)} out of 5`">
                  <Star
                    v-for="(filled, i) in ratingStars"
                    :key="i"
                    class="w-4 h-4"
                    :class="filled ? 'text-gold fill-gold' : 'text-muted/30'"
                    aria-hidden="true"
                  />
                </div>
                <span class="text-xs text-muted underline underline-offset-4">
                  {{ product.review_count }} {{ product.review_count === 1 ? 'review' : 'reviews' }}
                </span>
              </a>
            </template>
            <a v-else href="#reviews" class="text-xs text-muted hover:text-dark underline underline-offset-4 transition-colors">
              No reviews yet — be the first to review
            </a>
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

          <div v-if="inStock" class="flex flex-wrap items-stretch gap-3 mb-6">
            <div class="inline-flex shrink-0 items-center border border-primary/40 rounded-[14px] overflow-hidden" role="group" aria-label="Quantity">
              <button
                type="button" class="grid h-12 w-12 shrink-0 place-items-center hover:bg-primary/30 transition-colors disabled:opacity-40 focus-visible:outline-2 focus-visible:outline-offset-[-3px] focus-visible:outline-gold"
                aria-label="Decrease quantity"
                @click="decrementQty"
                :disabled="quantity <= 1"
              >
                <Minus class="w-4 h-4" />
              </button>
              <span class="w-10 shrink-0 text-sm font-medium text-center" aria-live="polite">{{ quantity }}</span>
              <button
                type="button" class="grid h-12 w-12 shrink-0 place-items-center hover:bg-primary/30 transition-colors disabled:opacity-40 focus-visible:outline-2 focus-visible:outline-offset-[-3px] focus-visible:outline-gold"
                aria-label="Increase quantity"
                @click="incrementQty"
                :disabled="quantity >= product.stock"
              >
                <Plus class="w-4 h-4" />
              </button>
            </div>

            <BaseButton
              variant="secondary"
              class="min-h-12 min-w-[10rem] flex-1"
              :loading="addingToCart"
              @click="handleAddToCart"
            >
              <template v-if="addedToCart">Added to Cart!</template>
              <template v-else>Add to Cart</template>
            </BaseButton>
          </div>
          <p v-if="cartError" role="alert" class="mt-2 text-sm text-red-700">{{ cartError }}</p>

          <div class="flex items-center gap-2 text-xs text-muted py-2 border-t border-primary/20">
            <button
              type="button"
              class="inline-flex min-h-11 items-center gap-1.5 hover:text-dark transition-colors active:scale-95 focus-visible:outline-2 focus-visible:outline-gold rounded-lg px-1"
              :aria-pressed="inWishlist"
              @click="handleToggleWishlist"
            >
              <Heart
                class="w-4 h-4 transition-all"
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
                <p class="text-xs text-muted">MTN Mobile Money and Airtel Money</p>
              </div>
            </div>
          </div>

          <section v-if="descriptionBlocks.length" aria-label="Product details" class="mt-7 border-t border-primary/20 pt-6">
            <h2 class="mb-4 font-heading text-lg font-semibold text-dark">Product details</h2>
            <div class="max-w-prose space-y-4 text-sm leading-7 text-muted break-words">
              <template v-for="(block, index) in descriptionBlocks" :key="index">
                <p v-if="block.type === 'paragraph'"><DescriptionInline :text="block.text" /></p>
                <h3 v-else-if="block.type === 'heading'" class="pt-1 text-sm font-semibold text-dark"><DescriptionInline :text="block.text" /></h3>
                <component :is="block.ordered ? 'ol' : 'ul'" v-else :class="block.ordered ? 'list-decimal' : 'list-disc'" class="space-y-1 pl-5 marker:text-gold"><li v-for="(item, itemIndex) in block.items" :key="itemIndex"><DescriptionInline :text="item" /></li></component>
              </template>
            </div>
          </section>
        </div>
      </div>

      <!-- Reviews Section -->
      <section id="reviews" class="mt-16 pt-8 border-t border-primary/20 scroll-mt-24">
        <h2 class="font-heading text-xl font-semibold text-dark mb-6">Customer Reviews</h2>

        <!-- Review Form -->
        <p v-if="userStore.isAuthenticated && ownReviewLoading" class="mb-6 text-sm text-muted" role="status">Checking your review…</p>
        <div v-else-if="userStore.isAuthenticated && ownReviewError" class="mb-6 text-sm text-red-700" role="alert">Could not load your review. <button type="button" class="underline" @click="loadOwnReview">Try again</button></div>
        <div v-else-if="userStore.isAuthenticated && ownReview && !editingReview" class="bg-white rounded-2xl p-5 border border-primary/20 mb-6">
          <div class="flex flex-wrap items-center justify-between gap-3"><h3 class="font-medium text-dark">Your review</h3><span class="text-xs font-medium text-muted">{{ ownReview.is_approved ? 'Published' : 'Awaiting approval' }}</span></div>
          <p class="mt-2 text-gold" :aria-label="`${ownReview.rating} out of 5 stars`">{{ '★'.repeat(ownReview.rating) }}{{ '☆'.repeat(5 - ownReview.rating) }}</p>
          <p class="mt-2 text-sm text-muted whitespace-pre-line break-words">{{ ownReview.comment }}</p>
          <p v-if="reviewError" role="alert" class="mt-3 text-sm text-red-700">{{ reviewError }}</p>
          <div class="mt-4 flex gap-4"><button type="button" class="text-sm font-medium underline underline-offset-4" @click="startEditing">Edit review</button><button type="button" class="text-sm text-muted underline underline-offset-4" :disabled="reviewSubmitting" @click="deleteOwnReview">Delete</button></div>
        </div>
        <div v-else-if="userStore.isAuthenticated" class="bg-white rounded-[16px] p-5 border border-primary/20 mb-6">
          <h3 class="text-sm font-medium text-dark mb-3">{{ editingReview ? 'Edit your review' : 'Write a review' }}</h3>
          <div class="flex items-center gap-1 mb-3" role="group" aria-label="Your rating">
            <button
              v-for="i in 5"
              :key="i"
              type="button"
              class="p-2"
              :aria-label="`${i} ${i === 1 ? 'star' : 'stars'}`"
              :aria-pressed="reviewRating === i"
              @click="reviewRating = i"
            >
              <Star
                class="w-5 h-5 transition-colors"
                :class="i <= reviewRating ? 'text-gold fill-gold' : 'text-muted/30'"
              />
            </button>
          </div>
          <div class="flex items-center justify-between mb-2">
            <label for="review-comment" class="block text-sm font-medium text-dark">Your review</label>
            <span class="text-xs text-muted tabular-nums">{{ reviewComment.trim().length }} / 1000</span>
          </div>
          <textarea id="review-comment"
            v-model="reviewComment"
            maxlength="1000"
            :aria-invalid="!!reviewError"
            :aria-describedby="reviewError ? 'review-error' : undefined"
            class="w-full px-4 py-3 bg-white border rounded-[14px] text-sm text-dark placeholder:text-muted/60 focus:outline-none focus:border-gold transition-colors"
            :class="reviewError ? 'border-red-600' : 'border-primary/40'"
            rows="3"
            placeholder="Share your experience with this product..."
            @input="reviewError = ''"
          />
          <p v-if="editingReview" class="mt-2 text-xs text-muted">Edited reviews are checked again before publication.</p>
          <button v-if="editingReview" type="button" class="mt-3 text-sm underline" @click="editingReview = false; reviewError = ''">Cancel editing</button>
          <div class="flex items-center justify-between gap-3 mt-3">
            <p v-if="reviewError" id="review-error" role="alert" class="text-sm text-red-700">{{ reviewError }}</p>
            <div v-else />
            <BaseButton size="sm" :loading="reviewSubmitting" @click="submitReview">
              <Send class="w-3.5 h-3.5 mr-1.5" /> {{ editingReview ? 'Save changes' : 'Submit review' }}
            </BaseButton>
          </div>
        </div>
        <div v-else class="text-center py-4 mb-6 bg-primary/10 rounded-[14px]">
          <p class="text-sm text-muted">
            <router-link :to="{ path: '/auth/login', query: { redirect: route.fullPath } }" class="text-gold hover:underline">Sign in</router-link> to write a review
          </p>
        </div>

        <!-- Reviews List -->
        <p v-if="productStore.reviewsLoading" class="text-sm text-muted py-6" role="status">Loading reviews…</p>
        <div v-else-if="productStore.reviewsError" class="text-sm text-muted py-6" role="alert">
          Reviews could not be loaded. <button type="button" class="underline text-dark" @click="productStore.fetchReviews(String(route.params.slug))">Try again</button>
        </div>
        <div v-else-if="productStore.reviews.length > 0" class="space-y-4">
          <div
            v-for="review in productStore.reviews.filter(item => item.id !== ownReview?.id)"
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
            <p class="text-sm text-muted leading-relaxed whitespace-pre-line">{{ review.comment }}</p>
            <div v-if="review.staff_reply" class="mt-4 ml-3 border-l-2 border-primary/40 bg-primary/10 rounded-r-xl px-4 py-3">
              <p class="text-xs font-semibold uppercase tracking-wide text-dark mb-1">Reply from By Nzuri</p>
              <p class="text-sm text-muted leading-relaxed whitespace-pre-line">{{ review.staff_reply }}</p>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-8 text-muted text-sm">
          No reviews yet. Share your experience to help others.
        </div>
      </section>

      <!-- Related Products -->
      <section v-if="filteredRelatedProducts.length > 0" class="mt-16">
        <h2 class="font-heading text-xl font-semibold text-dark mb-6">You May Also Like</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
          <ProductCard
            v-for="p in filteredRelatedProducts"
            :key="p.id"
            :product="p"
          />
        </div>
      </section>

      <!-- Recently Viewed -->
      <section v-if="filteredRecentlyViewed.length > 0" class="mt-16 mb-8">
        <h2 class="font-heading text-xl font-semibold text-dark mb-6">Recently Viewed</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
          <ProductCard
            v-for="p in filteredRecentlyViewed"
            :key="p.id"
            :product="p"
          />
        </div>
      </section>

      <!-- Sticky mobile add-to-cart bar -->
      <div
        v-if="inStock"
        class="md:hidden fixed bottom-0 inset-x-0 z-40 border-t border-primary/30 bg-background/95 backdrop-blur-md px-4 py-3 flex items-center justify-between gap-3 shadow-[0_-4px_20px_rgba(0,0,0,0.06)]"
      >
        <div class="min-w-0">
          <p class="text-xs text-muted truncate">{{ product.title }}</p>
          <p class="text-base font-bold text-dark tabular-nums">K{{ product.sale_price ?? product.price }}</p>
        </div>
        <BaseButton
          variant="secondary"
          class="min-h-11 shrink-0"
          :loading="addingToCart"
          @click="handleAddToCart"
        >
          {{ addedToCart ? 'Added!' : 'Add to Cart' }}
        </BaseButton>
      </div>
      <div v-if="inStock" class="h-16 md:hidden" aria-hidden="true" />
    </template>
  </div>
</template>
