<script setup lang="ts">
import { useWishlistStore } from '@/stores/wishlist'
import ProductCard from '@/components/product/ProductCard.vue'
import { Heart } from '@lucide/vue'

const wishlistStore = useWishlistStore()
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 py-8">
    <h1 class="font-heading text-2xl font-semibold text-dark mb-6">My Wishlist</h1>

    <div v-if="wishlistStore.items.length > 0" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
      <ProductCard
        v-for="item in wishlistStore.items"
        :key="item.id"
        :product="item.product"
      />
    </div>

    <div v-else class="mx-auto my-8 max-w-xl rounded-[28px] border border-primary/40 bg-gradient-to-b from-primary/20 to-background px-6 py-16 text-center sm:py-20">
      <div class="relative mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full border border-primary/60 bg-white/70">
        <span aria-hidden="true" class="absolute inset-1 rounded-full border border-primary/40" />
        <Heart aria-hidden="true" class="w-7 h-7 text-gold" />
      </div>
      <p class="mb-3 text-[10px] font-semibold uppercase tracking-[0.2em] text-muted">A little collection of favourites</p>
      <h2 class="font-heading text-xl font-medium text-dark mb-2">Your wishlist is waiting</h2>
      <p class="mx-auto max-w-xs text-sm leading-relaxed text-muted mb-6">Tap the heart on anything you love, and find it here when you’re ready.</p>
      <router-link to="/catalog" class="inline-flex min-h-11 items-center justify-center rounded-full bg-dark px-6 text-sm font-semibold text-background transition-colors hover:bg-dark/90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold">Browse products <span aria-hidden="true" class="ml-3">→</span></router-link>
    </div>
  </div>
</template>
