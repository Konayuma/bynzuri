import api, { publicApi } from './api'
import type { Product, Category, PaginatedResponse, ProductCreateData, ProductImage } from '@/types'

export interface SaleCampaign {
  title: string
  percent: string
  starts_on: string
  ends_on: string
  fulfilment: string
  enabled: boolean
  show_banner: boolean
}

export const productService = {
  async getCampaign(admin = false): Promise<SaleCampaign | null> {
    return (await (admin ? api : publicApi).get('/products/campaign/', { params: admin ? { admin: '1' } : undefined })).data
  },
  async saveCampaign(campaign: SaleCampaign): Promise<SaleCampaign> {
    return (await api.put('/products/campaign/', campaign)).data
  },
  async getStoreDiscount(): Promise<{ percent: string }> {
    return (await api.get('/products/store-discount/')).data
  },
  async setStoreDiscount(percent: string): Promise<{ percent: string }> {
    return (await api.put('/products/store-discount/', { percent })).data
  },
  async getProducts(params?: {
    page?: number
    search?: string
    category?: string
    ordering?: string
    min_price?: string
    max_price?: string
    in_stock?: boolean
  }): Promise<PaginatedResponse<Product>> {
    const response = await publicApi.get('/products/', { params: { ...params, category__slug: params?.category, category: undefined } })
    return response.data
  },

  async importSignatureCatalog(): Promise<{ created: string[]; skipped: string[] }> {
    const response = await api.post('/products/import-signature/')
    return response.data
  },

  async getManagedProducts(page: number): Promise<PaginatedResponse<Product>> {
    const response = await api.get('/products/manage/', { params: { page } })
    return response.data
  },

  async getProduct(slug: string): Promise<Product> {
    const response = await publicApi.get(`/products/${slug}/`)
    return response.data
  },

  async createCategory(name: string): Promise<Category> {
    const response = await api.post('/categories/', { name })
    return response.data
  },

  async getCategories(): Promise<Category[]> {
    const response = await publicApi.get('/categories/')
    return response.data
  },

  async getBestSellers(): Promise<Product[]> {
    const response = await publicApi.get('/products/best-sellers/')
    return response.data
  },

  async getNewArrivals(): Promise<Product[]> {
    const response = await publicApi.get('/products/new-arrivals/')
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
  },

  async uploadProductImage(slug: string, formData: FormData): Promise<ProductImage> {
    const response = await api.post(`/products/${slug}/images/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  async deleteProductImage(slug: string, imageId: string): Promise<void> {
    await api.delete(`/products/${slug}/images/${imageId}/`)
  },
}
