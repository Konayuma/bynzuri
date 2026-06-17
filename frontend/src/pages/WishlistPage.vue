<script setup lang="ts">
import { useWishlistStore } from '@/stores/wishlist'
import ProductCard from '@/components/product/ProductCard.vue'
import BaseButton from '@/components/base/BaseButton.vue'
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

    <div v-else class="text-center py-20">
      <div class="w-16 h-16 rounded-full bg-primary/30 flex items-center justify-center mx-auto mb-4">
        <Heart class="w-7 h-7 text-muted" />
      </div>
      <h2 class="font-heading text-lg font-medium text-dark mb-2">Your wishlist is empty</h2>
      <p class="text-sm text-muted mb-6">Save items you love to revisit them later.</p>
      <router-link to="/catalog">
        <BaseButton>Browse Products</BaseButton>
      </router-link>
    </div>
  </div>
</template>
