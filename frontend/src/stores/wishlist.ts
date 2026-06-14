import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Product, WishlistItem } from '@/types'

const STORAGE_KEY = 'bynzuri_wishlist'

export const useWishlistStore = defineStore('wishlist', () => {
  const items = ref<WishlistItem[]>([])

  const itemIds = computed(() => new Set(items.value.map(i => i.product.id)))
  const count = computed(() => items.value.length)

  function load() {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      try {
        items.value = JSON.parse(stored)
      } catch {
        items.value = []
      }
    }
  }

  function save() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items.value))
  }

  function isWishlisted(productId: string): boolean {
    return itemIds.value.has(productId)
  }

  function toggle(product: Product) {
    const existing = items.value.find(i => i.product.id === product.id)
    if (existing) {
      items.value = items.value.filter(i => i.id !== existing.id)
    } else {
      items.value.push({
        id: `wl_${Date.now()}`,
        product,
        added_at: new Date().toISOString()
      })
    }
    save()
  }

  function add(product: Product) {
    if (!isWishlisted(product.id)) {
      items.value.push({
        id: `wl_${Date.now()}`,
        product,
        added_at: new Date().toISOString()
      })
      save()
    }
  }

  function remove(productId: string) {
    items.value = items.value.filter(i => i.product.id !== productId)
    save()
  }

  load()

  return {
    items,
    count,
    itemIds,
    isWishlisted,
    toggle,
    add,
    remove
  }
})
