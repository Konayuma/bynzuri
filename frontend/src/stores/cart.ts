import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Cart, CartItem, Product } from '@/types'
import { cartService } from '@/services/cart.service'
import { hasSession } from '@/services/api'

export const useCartStore = defineStore('cart', () => {
  const cart = ref<Cart | null>(null)
  const loading = ref(false)
  const error = ref('')
  let cartRevision = 0

  const items = computed(() => cart.value?.items || [])
  const itemCount = computed(() => cart.value?.item_count || 0)
  const subtotal = computed(() => cart.value?.subtotal || '0.00')
  const total = computed(() => cart.value?.total || '0.00')

  function initGuestCart() {
    const stored = localStorage.getItem('guest_cart')
    if (stored) {
      try { cart.value = JSON.parse(stored) } catch { localStorage.removeItem('guest_cart') }
    }
  }

  function saveGuestCart() {
    if (cart.value) {
      localStorage.setItem('guest_cart', JSON.stringify(cart.value))
    }
  }

  async function fetchCart() {
    const revision = cartRevision
    loading.value = true
    const previousError = error.value.startsWith('Some items could not be added') ? error.value : ''
    error.value = ''
    try {
      const data = await cartService.getCart()
      if (revision === cartRevision) { cart.value = data; error.value = previousError }
    } catch {
      if (revision === cartRevision) error.value = 'Could not load your cart. Please check your connection and try again.'
    } finally {
      loading.value = false
    }
  }

  async function addToCart(product: Product, quantity: number = 1) {
    cartRevision++
    error.value = ''
    const existingQuantity = items.value.find(item => item.product.id === product.id)?.quantity || 0
    if (!product.is_in_stock || !Number.isInteger(quantity) || quantity < 1 || existingQuantity + quantity > product.stock) {
      error.value = 'This product is unavailable in the requested quantity.'
      throw new Error(error.value)
    }
    const token = hasSession()
    if (token) {
      loading.value = true
      try {
        const data = await cartService.addItem(product.id, quantity)
        cart.value = data
      } catch (cause) {
        error.value = 'Could not add this product. Check your connection or sign in again, then retry.'
        throw cause
      } finally {
        loading.value = false
      }
    } else {
      addToGuestCart(product, quantity)
    }
  }

  function addToGuestCart(product: Product, quantity: number) {
    if (!cart.value) {
      cart.value = { id: '', items: [], subtotal: '0.00', total: '0.00', item_count: 0 }
    }

    const existing = cart.value.items.find(item => item.product.id === product.id)
    if (existing) {
      existing.quantity += quantity
    } else {
      cart.value.items.push({
        id: `guest_${crypto.randomUUID()}`,
        product,
        quantity,
        total_price: (parseFloat(product.price) * quantity).toFixed(2)
      })
    }

    recalculateGuestCart()
    saveGuestCart()
  }

  async function updateQuantity(itemId: string, quantity: number) {
    error.value = ''
    const token = hasSession()
    if (token) {
      loading.value = true
      try {
        const data = await cartService.updateItem(itemId, quantity)
        cart.value = data
      } catch (cause) {
        error.value = 'Could not update your cart. Check stock and your connection, then try again.'
        throw cause
      } finally {
        loading.value = false
      }
    } else {
      const item = cart.value?.items.find(i => i.id === itemId)
      if (item) {
        if (!Number.isInteger(quantity) || quantity < 1 || !item.product.is_in_stock || quantity > item.product.stock) {
          error.value = 'This product is unavailable in the requested quantity.'
          throw new Error(error.value)
        }
        item.quantity = quantity
        recalculateGuestCart()
        saveGuestCart()
      }
    }
  }

  async function removeItem(itemId: string) {
    cartRevision++
    error.value = ''
    const token = hasSession()
    if (token) {
      loading.value = true
      try {
        const data = await cartService.removeItem(itemId)
        cart.value = data
      } catch (cause) {
        error.value = 'Could not remove this item. Check your connection and try again.'
        throw cause
      } finally {
        loading.value = false
      }
    } else {
      if (cart.value) {
        cart.value.items = cart.value.items.filter(i => i.id !== itemId)
        recalculateGuestCart()
        saveGuestCart()
      }
    }
  }

  function recalculateGuestCart() {
    if (!cart.value) return
    for (const item of cart.value.items) item.total_price = (parseFloat(item.product.price) * item.quantity).toFixed(2)
    const subtotal = cart.value.items.reduce(
      (sum, item) => sum + parseFloat(item.product.price) * item.quantity, 0
    )
    cart.value.subtotal = subtotal.toFixed(2)
    cart.value.total = subtotal.toFixed(2)
    cart.value.item_count = cart.value.items.reduce((sum, item) => sum + item.quantity, 0)
  }

  function clearCart() {
    cart.value = null
    localStorage.removeItem('guest_cart')
  }

  async function mergeGuestCart() {
    const stored = localStorage.getItem('guest_cart')
    if (!stored) return

    const guestCart = JSON.parse(stored)
    if (guestCart.items.length > 0) {
      const items = guestCart.items.map((item: CartItem) => ({
        product: item.product.id,
        quantity: item.quantity
      }))
      const data = await cartService.mergeCart(items)
      cart.value = data
      const skipped = (data as Cart & { skipped?: { index: number; reason: string }[] }).skipped || []
      if (skipped.length) {
        guestCart.items = skipped.map(entry => guestCart.items[entry.index]).filter(Boolean)
        localStorage.setItem('guest_cart', JSON.stringify(guestCart))
        error.value = 'Some items could not be added because they are unavailable or exceed available stock.'
      } else localStorage.removeItem('guest_cart')
    }
  }

  return {
    cart,
    loading,
    error,
    items,
    itemCount,
    subtotal,
    total,
    fetchCart,
    addToCart,
    updateQuantity,
    removeItem,
    clearCart,
    mergeGuestCart,
    initGuestCart
  }
})
