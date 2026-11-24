import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useCartStore } from '@/stores/cart'
import { cartService } from '@/services/cart.service'
import { clearSession, setAccessToken } from '@/services/api'
import type { Cart, Product } from '@/types'

const product: Product = { id: 'p', category: 'c', category_name: 'Care', title: 'Oil', slug: 'oil', description: '', price: '10.00', stock: 5, is_in_stock: true, images: [], rating: 0, review_count: 0, created_at: '' }
const empty: Cart = { id: 'c', items: [], subtotal: '0.00', total: '0.00', item_count: 0 }
const filled: Cart = { ...empty, items: [{ id: 'i', product, quantity: 1, total_price: '10.00' }], item_count: 1, subtotal: '10.00', total: '10.00' }

describe('cart recovery', () => {
  beforeEach(() => { setActivePinia(createPinia()); localStorage.clear(); setAccessToken('token') })
  afterEach(() => { clearSession(); vi.restoreAllMocks() })
  it('does not replace a successful add with an older cart response', async () => {
    let resolveFetch!: (cart: Cart) => void
    vi.spyOn(cartService, 'getCart').mockReturnValue(new Promise(resolve => { resolveFetch = resolve }))
    vi.spyOn(cartService, 'addItem').mockResolvedValue(filled)
    const store = useCartStore()
    const fetching = store.fetchCart()
    await store.addToCart(product)
    resolveFetch(empty)
    await fetching
    expect(store.items).toHaveLength(1)
  })
  it('exposes an add failure instead of treating it as success', async () => {
    vi.spyOn(cartService, 'addItem').mockRejectedValue(new Error('offline'))
    const store = useCartStore()
    await expect(store.addToCart(product)).rejects.toThrow('offline')
    expect(store.error).toContain('Could not add')
    expect(store.items).toHaveLength(0)
  })
})
