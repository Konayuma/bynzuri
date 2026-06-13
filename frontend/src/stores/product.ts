import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Product, Category, PaginatedResponse } from '@/types'
import { productService } from '@/services/product.service'

export const useProductStore = defineStore('product', () => {
  const products = ref<Product[]>([])
  const categories = ref<Category[]>([])
  const bestSellers = ref<Product[]>([])
  const newArrivals = ref<Product[]>([])
  const currentProduct = ref<Product | null>(null)
  const relatedProducts = ref<Product[]>([])
  const loading = ref(false)
  const pagination = ref<Pick<PaginatedResponse<Product>, 'count' | 'next' | 'previous'>>({
    count: 0,
    next: null,
    previous: null
  })

  async function fetchProducts(params?: {
    page?: number
    search?: string
    category?: string
    ordering?: string
  }) {
    loading.value = true
    try {
      const data = await productService.getProducts(params)
      products.value = data.results
      pagination.value = { count: data.count, next: data.next, previous: data.previous }
    } finally {
      loading.value = false
    }
  }

  async function fetchProduct(slug: string) {
    loading.value = true
    try {
      currentProduct.value = await productService.getProduct(slug)
    } finally {
      loading.value = false
    }
  }

  async function fetchRelatedProducts(categorySlug?: string) {
    if (!categorySlug) return
    try {
      const data = await productService.getProducts({ category: categorySlug })
      relatedProducts.value = data.results.slice(0, 4)
    } catch {
      // silently fail
    }
  }

  async function fetchCategories() {
    try {
      categories.value = await productService.getCategories()
    } catch {
      // silently fail
    }
  }

  async function fetchBestSellers() {
    try {
      bestSellers.value = await productService.getBestSellers()
    } catch {
      // silently fail
    }
  }

  async function fetchNewArrivals() {
    try {
      newArrivals.value = await productService.getNewArrivals()
    } catch {
      // silently fail
    }
  }

  return {
    products,
    categories,
    bestSellers,
    newArrivals,
    currentProduct,
    relatedProducts,
    loading,
    pagination,
    fetchProducts,
    fetchProduct,
    fetchRelatedProducts,
    fetchCategories,
    fetchBestSellers,
    fetchNewArrivals
  }
})
