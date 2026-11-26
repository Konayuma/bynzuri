import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useWishlistStore } from '@/stores/wishlist'

describe('wishlist recovery', () => {
  beforeEach(() => { localStorage.clear(); setActivePinia(createPinia()) })

  it('keeps valid entries usable if stored products are missing', () => {
    localStorage.setItem('bynzuri_wishlist', JSON.stringify([null, { id: 'bad', product: null }, { id: 'good', product: { id: 'p1', title: 'Oil', slug: 'oil' }, added_at: '2026-01-01' }]))
    const store = useWishlistStore()
    expect(store.count).toBe(1)
    expect(store.isWishlisted('p1')).toBe(true)
    expect(store.isWishlisted('other')).toBe(false)
  })
})
