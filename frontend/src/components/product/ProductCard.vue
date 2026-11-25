<script setup lang="ts">
import type { Product } from '@/types'
import { useCartStore } from '@/stores/cart'
import { useWishlistStore } from '@/stores/wishlist'
import { useUIStore } from '@/stores/ui'
import { Check, Heart, ShoppingBag } from '@lucide/vue'
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { signatureImage } from '@/utils/productImage'

const props = defineProps<{
  product: Product
}>()

const cartStore = useCartStore()
const uiStore = useUIStore()
const cartError = ref('')
const adding = ref(false)
const added = ref(false)
let addedTimer: ReturnType<typeof setTimeout> | undefined
const wishlistStore = useWishlistStore()
const imageFailed = ref(false)
const fallbackFailed = ref(false)
const imageLoading = ref(true)
const localProductImage = computed(() => !imageFailed.value && props.product.images?.[0]?.image || (!fallbackFailed.value && signatureImage(props.product.slug)) || undefined)
watch(() => props.product, () => { imageFailed.value = false; fallbackFailed.value = false; imageLoading.value = true })
onBeforeUnmount(() => { if (addedTimer) clearTimeout(addedTimer) })

function handleImageError() {
  if (!imageFailed.value && props.product.images?.[0]?.image) imageFailed.value = true
  else fallbackFailed.value = true
  imageLoading.value = Boolean(localProductImage.value)
}

async function handleAddToCart(e: Event) {
  e.stopPropagation()
  if (adding.value || !props.product.is_in_stock) return
  adding.value = true
  cartError.value = ''
  try {
    await cartStore.addToCart(props.product)
    added.value = true
    uiStore.showToast(`Added ${props.product.title} to your bag`, {
      actionLabel: 'View bag',
      onAction: () => uiStore.openCart(),
    })
    if (addedTimer) clearTimeout(addedTimer)
    addedTimer = setTimeout(() => { added.value = false }, 1500)
  } catch {
    cartError.value = cartStore.error
  } finally {
    adding.value = false
  }
}

function handleToggleWishlist(e: Event) {
  e.stopPropagation()
  wishlistStore.toggle(props.product)
}

</script>

<template>
  <div class="group flex flex-col h-full">
    <div class="relative aspect-[3/4] rounded-[20px] overflow-hidden bg-primary/20 mb-2.5 sm:mb-3">
      <router-link :to="`/product/${product.slug}`" :aria-label="`View ${product.title}`" class="block w-full h-full focus-visible:outline-2 focus-visible:outline-offset-[-3px] focus-visible:outline-gold">
        <div v-if="localProductImage && imageLoading" class="absolute inset-0 bg-primary/30 motion-safe:animate-pulse pointer-events-none" aria-hidden="true" />
        <img
          v-if="localProductImage"
          :src="localProductImage"
          :alt="product.title"
          class="relative w-full h-full object-cover motion-safe:transition-transform motion-safe:duration-500 motion-safe:ease-out motion-safe:group-hover:scale-[1.03]"
          :class="{ 'opacity-0': imageLoading }"
          loading="lazy"
          decoding="async"
          @load="imageLoading = false"
          @error="handleImageError"
        />
        <div v-else class="w-full h-full flex items-center justify-center text-muted">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>
        </div>
      </router-link>

      <div
        v-if="!product.is_in_stock"
        class="pointer-events-none absolute inset-0 bg-black/40 flex items-center justify-center"
      >
        <span class="bg-background text-dark text-xs font-semibold px-4 py-1.5 rounded-full">
          Out of Stock
        </span>
      </div>
    </div>

    <div class="flex items-start justify-between gap-1.5 mb-0.5">
      <p class="text-[11px] sm:text-xs text-muted uppercase tracking-wider truncate pt-1">
        {{ product.category_name }}
      </p>
      <button
        type="button"
        class="shrink-0 -mt-1 -mr-1.5 w-11 h-11 rounded-full flex items-center justify-center hover:bg-primary/25 transition-colors motion-safe:active:scale-90 focus-visible:outline-2 focus-visible:outline-gold"
        @click="handleToggleWishlist"
        :aria-label="wishlistStore.isWishlisted(product.id) ? 'Remove from wishlist' : 'Add to wishlist'"
        :aria-pressed="wishlistStore.isWishlisted(product.id)"
      >
        <Heart
          class="w-4 h-4 motion-safe:transition-transform motion-safe:duration-200"
          :class="wishlistStore.isWishlisted(product.id) ? 'text-red-500 fill-red-500 scale-110' : 'text-dark'"
        />
      </button>
    </div>

    <h3 class="text-sm font-medium text-dark leading-snug mb-1 line-clamp-2">
      <router-link :to="`/product/${product.slug}`" class="hover:text-gold transition-colors focus-visible:outline-2 focus-visible:outline-gold">
        {{ product.title }}
      </router-link>
    </h3>
    <p class="text-sm font-bold text-dark tabular-nums">
      <span v-if="Number(product.effective_discount_percent ?? product.discount_percent) > 0" class="mr-1.5 font-normal text-muted line-through">K{{ product.price }}</span>K{{ product.sale_price ?? product.price }}
    </p>

    <div class="mt-auto pt-3">
      <button
        type="button"
        class="w-full min-h-10 sm:min-h-11 px-3 rounded-full text-xs sm:text-sm font-semibold tracking-wide flex items-center justify-center gap-2 transition-all active:scale-[0.97] disabled:opacity-45 disabled:cursor-not-allowed focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold"
        :class="added
          ? 'bg-success text-white'
          : 'bg-dark text-background hover:bg-dark/90'"
        :disabled="adding || !product.is_in_stock"
        :aria-busy="adding || undefined"
        :aria-label="!product.is_in_stock ? `${product.title} is out of stock` : `Add ${product.title} to cart`"
        @click="handleAddToCart"
      >
        <Check v-if="added" class="w-4 h-4 shrink-0 motion-safe:animate-[cart-confirm_300ms_ease-out]" aria-hidden="true" />
        <ShoppingBag v-else-if="product.is_in_stock" class="w-4 h-4 shrink-0" aria-hidden="true" />
        <span class="truncate">{{ !product.is_in_stock ? 'Out of Stock' : adding ? 'Adding…' : added ? 'Added to Cart' : 'Add to Cart' }}</span>
      </button>
    </div>

    <span class="sr-only" aria-live="polite">{{ added ? `${product.title} added to cart` : '' }}</span>
    <p v-if="cartError" role="alert" class="mt-1.5 text-xs sm:text-sm text-red-700">{{ cartError }}</p>
  </div>
</template>

<style scoped>
@keyframes cart-confirm {
  from { opacity: 0; transform: scale(.7); }
  to { opacity: 1; transform: scale(1); }
}
</style>
