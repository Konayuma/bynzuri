import api from './api'
import type { Review } from '@/types'

export const reviewService = {
  async getReviews(productSlug: string): Promise<Review[]> {
    const response = await api.get('/reviews/', { params: { product: productSlug } })
    return response.data.results || response.data
  },

  async createReview(data: {
    product_slug: string
    rating: number
    comment: string
  }): Promise<Review> {
    const response = await api.post('/reviews/', data)
    return response.data
  },
}
