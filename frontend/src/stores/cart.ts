import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Cart, CartItem, Product } from '@/types'
import { cartService } from '@/services/cart.service'

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
    error.value = ''
    try {
      const data = await cartService.getCart()
      if (revision === cartRevision) cart.value = data
    } catch {
      if (revision === cartRevision) error.value = 'Could not load your cart. Please check your connection and try again.'
    } finally {
      loading.value = false
    }
  }

  async function addToCart(product: Product, quantity: number = 1) {
    cartRevision++
    error.value = ''
    const token = localStorage.getItem('access_token')
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
        id: `guest_${Date.now()}`,
        product,
        quantity,
        total_price: (parseFloat(product.price) * quantity).toFixed(2)
      })
    }

    recalculateGuestCart()
    saveGuestCart()
  }

  async function updateQuantity(itemId: string, quantity: number) {
    const token = localStorage.getItem('access_token')
    if (token) {
      loading.value = true
      try {
        const data = await cartService.updateItem(itemId, quantity)
        cart.value = data
      } finally {
        loading.value = false
      }
    } else {
      const item = cart.value?.items.find(i => i.id === itemId)
      if (item) {
        item.quantity = quantity
        recalculateGuestCart()
        saveGuestCart()
      }
    }
  }

  async function removeItem(itemId: string) {
    const token = localStorage.getItem('access_token')
    if (token) {
      loading.value = true
      try {
        await cartService.removeItem(itemId)
        await fetchCart()
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
      localStorage.removeItem('guest_cart')
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
