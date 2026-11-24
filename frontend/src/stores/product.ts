import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Product, Category, Review, PaginatedResponse } from '@/types'
import { productService } from '@/services/product.service'
import { reviewService } from '@/services/review.service'

export const useProductStore = defineStore('product', () => {
  const products = ref<Product[]>([])
  const categories = ref<Category[]>([])
  const categoriesLoading = ref(false)
  const categoriesError = ref(false)
  const bestSellers = ref<Product[]>([])
  const newArrivals = ref<Product[]>([])
  const currentProduct = ref<Product | null>(null)
  const relatedProducts = ref<Product[]>([])
  const reviews = ref<Review[]>([])
  const loading = ref(false)
  const pagination = ref<Pick<PaginatedResponse<Product>, 'count' | 'next' | 'previous'>>({
    count: 0,
    next: null,
    previous: null
  })

  let categoriesFetched = false
  let catalogRequest = 0
  let productRequest = 0
  let reviewRequest = 0
  let relatedRequest = 0

  async function fetchProducts(params?: {
    page?: number
    search?: string
    category?: string
    ordering?: string
    min_price?: string
    max_price?: string
    in_stock?: boolean
  }) {
    const request = ++catalogRequest
    loading.value = true
    try {
      const data = await productService.getProducts(params)
      if (request === catalogRequest) {
        products.value = data.results
        pagination.value = { count: data.count, next: data.next, previous: data.previous }
      }
    } catch (error) {
      if (request === catalogRequest) throw error
    } finally {
      if (request === catalogRequest) loading.value = false
    }
  }

  async function fetchProduct(slug: string) {
    const request = ++productRequest
    loading.value = true
    currentProduct.value = null
    relatedProducts.value = []
    ++relatedRequest
    try {
      const product = await productService.getProduct(slug)
      if (request === productRequest) currentProduct.value = product
    } finally {
      if (request === productRequest) loading.value = false
    }
  }

  async function fetchRelatedProducts(categorySlug?: string) {
    const request = ++relatedRequest
    relatedProducts.value = []
    if (!categorySlug) return
    try {
      const data = await productService.getProducts({ category: categorySlug, page_size: 4 } as Parameters<typeof productService.getProducts>[0])
      if (request === relatedRequest) relatedProducts.value = data.results.slice(0, 4)
    } catch {
      if (request === relatedRequest) relatedProducts.value = []
    }
  }

  async function fetchCategories() {
    if (categoriesFetched && categories.value.length > 0) return
    if (categoriesLoading.value) return
    categoriesLoading.value = true
    categoriesError.value = false
    try {
      categories.value = await productService.getCategories()
      categoriesFetched = true
    } catch {
      categoriesError.value = true
    } finally {
      categoriesLoading.value = false
    }
  }

  async function fetchBestSellers() {
    if (bestSellers.value.length > 0) return
    try {
      bestSellers.value = await productService.getBestSellers()
    } catch {
      // silently fail
    }
  }

  async function fetchNewArrivals() {
    if (newArrivals.value.length > 0) return
    try {
      newArrivals.value = await productService.getNewArrivals()
    } catch {
      // silently fail
    }
  }

  async function fetchReviews(productSlug: string) {
    const request = ++reviewRequest
    reviews.value = []
    try {
      const result = await reviewService.getReviews(productSlug)
      if (request === reviewRequest) reviews.value = result
    } catch {
      if (request === reviewRequest) reviews.value = []
    }
  }

  async function createReview(data: { product_slug: string; rating: number; comment: string }) {
    const review = await reviewService.createReview(data)
    reviews.value.unshift(review)
    return review
  }

  return {
    products,
    categories,
    categoriesLoading,
    categoriesError,
    bestSellers,
    newArrivals,
    currentProduct,
    relatedProducts,
    reviews,
    loading,
    pagination,
    fetchProducts,
    fetchProduct,
    fetchRelatedProducts,
    fetchCategories,
    fetchBestSellers,
    fetchNewArrivals,
    fetchReviews,
    createReview
  }
})
