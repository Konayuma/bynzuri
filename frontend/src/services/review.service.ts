import api, { publicApi } from './api'
import type { Review } from '@/types'

export const reviewService = {
  async getReviews(productSlug: string): Promise<Review[]> {
    const reviews: Review[] = []
    let page = 1
    while (true) {
      const response = await publicApi.get('/reviews/', { params: { product: productSlug, page } })
      if (Array.isArray(response.data)) return response.data
      reviews.push(...response.data.results)
      if (!response.data.next) return reviews
      page++
    }
  },

  async getMine(productSlug: string): Promise<Review | null> {
    const response = await api.get('/reviews/', { params: { product: productSlug, mine: '1' } })
    return (response.data.results || response.data)[0] || null
  },
  async updateReview(id: string, data: { rating: number; comment: string }): Promise<Review> {
    const response = await api.patch(`/reviews/${id}/`, data)
    return response.data
  },
  async deleteReview(id: string): Promise<void> {
    await api.delete(`/reviews/${id}/`)
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
