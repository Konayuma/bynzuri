import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useCartStore } from '@/stores/cart'
import { cartService } from '@/services/cart.service'
import { clearSession, setAccessToken } from '@/services/api'

function createMockProduct(id: string = 'p-1') {
  return {
    id,
    category: 'c-1',
    category_name: 'Oils',
    title: 'Test Oil',
    slug: 'test-oil',
    description: 'Test product',
    price: '99.99',
    stock: 10,
    is_in_stock: true,
    images: [],
    rating: 4.0,
    review_count: 2,
    created_at: '2026-01-01T00:00:00Z'
  }
}

describe('CartStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('starts with empty cart', () => {
    const store = useCartStore()
    expect(store.itemCount).toBe(0)
    expect(store.items).toEqual([])
  })

  it('adds item to guest cart', () => {
    const store = useCartStore()
    const product = createMockProduct()

    store.addToCart(product, 2)

    expect(store.itemCount).toBe(2)
    expect(store.items).toHaveLength(1)
    expect(store.items[0].product.id).toBe('p-1')
  })

  it('increases quantity when adding same product', () => {
    const store = useCartStore()
    const product = createMockProduct()

    store.addToCart(product, 1)
    store.addToCart(product, 3)

    expect(store.itemCount).toBe(4)
    expect(store.items[0].quantity).toBe(4)
  })

  it('removes item from cart', () => {
    const store = useCartStore()
    const product = createMockProduct()
    store.addToCart(product, 1)

    const itemId = store.items[0].id
    store.removeItem(itemId)

    expect(store.items).toHaveLength(0)
    expect(store.itemCount).toBe(0)
  })

  it('updates item quantity', () => {
    const store = useCartStore()
    const product = createMockProduct()
    store.addToCart(product, 1)

    const itemId = store.items[0].id
    store.updateQuantity(itemId, 5)

    expect(store.items[0].quantity).toBe(5)
    expect(store.items[0].total_price).toBe('499.95')
    expect(store.itemCount).toBe(5)
  })

  it('uses unique identifiers for guest items created together', async () => {
    const store = useCartStore()
    await store.addToCart(createMockProduct('p-1'))
    await store.addToCart(createMockProduct('p-2'))
    expect(store.items[0].id).not.toBe(store.items[1].id)
  })

  it('rejects guest quantities above stock', async () => {
    const store = useCartStore()
    await expect(store.addToCart(createMockProduct(), 11)).rejects.toThrow('unavailable')
    expect(store.items).toHaveLength(0)
  })

  it('retains guest lines skipped by a partial server merge', async () => {
    const store = useCartStore()
    await store.addToCart(createMockProduct('p-1'))
    await store.addToCart(createMockProduct('p-2'))
    vi.spyOn(cartService, 'mergeCart').mockResolvedValue({ id: 'server', items: [], subtotal: '0.00', total: '0.00', item_count: 0, skipped: [{ index: 1, reason: 'Unavailable' }] } as never)
    await store.mergeGuestCart()
    const remaining = JSON.parse(localStorage.getItem('guest_cart')!)
    expect(remaining.items.map((item: { product: { id: string } }) => item.product.id)).toEqual(['p-2'])
    expect(store.error).toContain('Some items could not be added')
    vi.restoreAllMocks()
  })

  it('calculates subtotal correctly', () => {
    const store = useCartStore()
    store.addToCart(createMockProduct('p-1'), 2)
    store.addToCart(createMockProduct('p-2'), 3)

    expect(store.subtotal).toBe((99.99 * 5).toFixed(2))
  })

  it('clears cart', () => {
    const store = useCartStore()
    store.addToCart(createMockProduct(), 1)
    store.clearCart()

    expect(store.cart).toBeNull()
    expect(store.itemCount).toBe(0)
  })

  it('persists guest cart to localStorage', () => {
    const store = useCartStore()
    const product = createMockProduct()
    store.addToCart(product, 2)

    const stored = localStorage.getItem('guest_cart')
    expect(stored).toBeTruthy()
    const parsed = JSON.parse(stored!)
    expect(parsed.item_count).toBe(2)
  })

  it('restores guest cart from localStorage', () => {
    const product = createMockProduct()
    const cartData = {
      id: '',
      items: [{ id: 'restored-1', product, quantity: 3, total_price: '299.97' }],
      subtotal: '299.97',
      total: '299.97',
      item_count: 3
    }
    localStorage.setItem('guest_cart', JSON.stringify(cartData))

    const store = useCartStore()
    store.initGuestCart()

    expect(store.itemCount).toBe(3)
    expect(store.items[0].quantity).toBe(3)
  })

  it('uses the cart returned by DELETE without triggering a second fetchCart call', async () => {
    setAccessToken('tok-123')
    const updatedCart = { id: 'cart-1', items: [], subtotal: '0.00', total: '0.00', item_count: 0 }
    const removeSpy = vi.spyOn(cartService, 'removeItem').mockResolvedValue(updatedCart)
    const getSpy = vi.spyOn(cartService, 'getCart')

    const store = useCartStore()
    await store.removeItem('item-1')

    expect(removeSpy).toHaveBeenCalledWith('item-1')
    expect(getSpy).not.toHaveBeenCalled()
    expect(store.cart).toEqual(updatedCart)

    clearSession()
    removeSpy.mockRestore()
    getSpy.mockRestore()
  })
})
