import api from './api'
import type { Product, Category, PaginatedResponse, ProductCreateData } from '@/types'

export const productService = {
  async getProducts(params?: {
    page?: number
    search?: string
    category?: string
    ordering?: string
  }): Promise<PaginatedResponse<Product>> {
    const response = await api.get('/products/', { params })
    return response.data
  },

  async getProduct(slug: string): Promise<Product> {
    const response = await api.get(`/products/${slug}/`)
    return response.data
  },

  async getCategories(): Promise<Category[]> {
    const response = await api.get('/categories/')
    return response.data
  },

  async getBestSellers(): Promise<Product[]> {
    const response = await api.get('/products/best-sellers/')
    return response.data
  },

  async getNewArrivals(): Promise<Product[]> {
    const response = await api.get('/products/new-arrivals/')
    return response.data
  },

  async createProduct(data: ProductCreateData): Promise<Product> {
    const response = await api.post('/products/', data)
    return response.data
  },

  async updateProduct(slug: string, data: Partial<ProductCreateData>): Promise<Product> {
    const response = await api.patch(`/products/${slug}/`, data)
    return response.data
  },

  async deleteProduct(slug: string): Promise<void> {
    await api.delete(`/products/${slug}/`)
  }
}
