<script setup lang="ts">
import type { Product } from '@/types'
import { useCartStore } from '@/stores/cart'
import { useWishlistStore } from '@/stores/wishlist'
import { Heart, ShoppingBag } from '@lucide/vue'
import { useRouter } from 'vue-router'
import { computed } from 'vue'
import { signatureImage } from '@/utils/productImage'

const props = defineProps<{
  product: Product
}>()

const cartStore = useCartStore()
const wishlistStore = useWishlistStore()
const router = useRouter()
const localProductImage = computed(() => props.product.images?.[0]?.image || signatureImage(props.product.slug))

function handleAddToCart(e: Event) {
  e.stopPropagation()
  cartStore.addToCart(props.product)
}

function handleToggleWishlist(e: Event) {
  e.stopPropagation()
  wishlistStore.toggle(props.product)
}

function goToProduct() {
  router.push(`/product/${props.product.slug}`)
}
</script>

<template>
  <div
    class="group cursor-pointer"
    @click="goToProduct"
  >
    <div class="relative aspect-[3/4] rounded-[20px] overflow-hidden bg-primary/20 mb-3">
      <img
        v-if="localProductImage"
        :src="localProductImage"
        :alt="product.title"
        class="w-full h-full object-cover transition-transform duration-[300ms] ease-[ease] group-hover:scale-[1.02]"
        loading="lazy"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-muted">
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>
      </div>

      <div class="absolute top-3 right-3 flex flex-col gap-2">
        <button
          class="w-9 h-9 rounded-full bg-background/90 backdrop-blur-sm flex items-center justify-center hover:bg-background transition-all shadow-sm active:scale-90"
          @click="handleToggleWishlist"
          :aria-label="wishlistStore.isWishlisted(product.id) ? 'Remove from wishlist' : 'Add to wishlist'"
        >
          <Heart
            class="w-4 h-4 transition-all"
            :class="wishlistStore.isWishlisted(product.id) ? 'text-red-500 fill-red-500' : 'text-dark'"
          />
        </button>
        <button
          class="w-9 h-9 rounded-full bg-background/90 backdrop-blur-sm flex items-center justify-center hover:bg-background transition-colors shadow-sm active:scale-90"
          @click="handleAddToCart"
          aria-label="Add to cart"
        >
          <ShoppingBag class="w-4 h-4 text-dark" />
        </button>
      </div>

      <div
        v-if="!product.is_in_stock"
        class="absolute inset-0 bg-black/40 flex items-center justify-center"
      >
        <span class="bg-background text-dark text-xs font-semibold px-4 py-1.5 rounded-full">
          Out of Stock
        </span>
      </div>
    </div>

    <p class="text-xs text-muted uppercase tracking-wider mb-1">{{ product.category_name }}</p>
    <h3 class="text-sm font-medium text-dark leading-snug mb-1">{{ product.title }}</h3>
    <p class="text-sm font-bold text-dark">K{{ product.price }}</p>
  </div>
</template>
