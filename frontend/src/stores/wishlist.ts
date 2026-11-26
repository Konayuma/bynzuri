import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Product, WishlistItem } from '@/types'

const STORAGE_KEY = 'bynzuri_wishlist'

export const useWishlistStore = defineStore('wishlist', () => {
  const items = ref<WishlistItem[]>([])
  let loaded = false

  const itemIds = computed(() => {
    ensureLoaded()
    return new Set(items.value.map(i => i.product.id))
  })
  const count = computed(() => {
    ensureLoaded()
    return items.value.length
  })

  function ensureLoaded() {
    if (loaded) return
    loaded = true
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (!stored) return
      const parsed: unknown = JSON.parse(stored)
      items.value = Array.isArray(parsed) ? parsed.filter((item): item is WishlistItem =>
        !!item && typeof item === 'object' && typeof item.id === 'string' &&
        !!item.product && typeof item.product === 'object' && typeof item.product.id === 'string' &&
        typeof item.product.title === 'string' && typeof item.product.slug === 'string'
      ) : []
    } catch { items.value = [] }
  }

  function save() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(items.value)) } catch { /* Keep the current session usable. */ }
  }

  function isWishlisted(productId: string): boolean {
    ensureLoaded()
    return itemIds.value.has(productId)
  }

  function toggle(product: Product) {
    ensureLoaded()
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
    ensureLoaded()
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
    ensureLoaded()
    items.value = items.value.filter(i => i.product.id !== productId)
    save()
  }

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
