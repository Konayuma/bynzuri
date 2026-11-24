import api from './api'
import type { Cart } from '@/types'

export const cartService = {
  async getCart(): Promise<Cart> {
    const response = await api.get('/cart/')
    return response.data
  },

  async addItem(productId: string, quantity: number = 1): Promise<Cart> {
    const response = await api.post('/cart/add/', { product: productId, quantity })
    return response.data
  },

  async updateItem(itemId: string, quantity: number): Promise<Cart> {
    const response = await api.patch(`/cart/items/${itemId}/`, { quantity })
    return response.data
  },

  async removeItem(itemId: string): Promise<Cart> {
    const response = await api.delete(`/cart/items/${itemId}/`)
    return response.data
  },

  async mergeCart(items: { product: string; quantity: number }[]): Promise<Cart> {
    const response = await api.post('/cart/merge/', { items })
    return response.data
  },

  async clearCart(): Promise<void> {
    await api.delete('/cart/')
  }
}
