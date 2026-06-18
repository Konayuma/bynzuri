import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Product, Category, Review, PaginatedResponse } from '@/types'
import { productService } from '@/services/product.service'
import { reviewService } from '@/services/review.service'

export const useProductStore = defineStore('product', () => {
  const products = ref<Product[]>([])
  const categories = ref<Category[]>([])
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
      const data = await productService.getProducts({ category: categorySlug, page_size: 4 } as Parameters<typeof productService.getProducts>[0])
      relatedProducts.value = data.results.slice(0, 4)
    } catch {
      // silently fail
    }
  }

  async function fetchCategories() {
    if (categoriesFetched && categories.value.length > 0) return
    try {
      categories.value = await productService.getCategories()
      categoriesFetched = true
    } catch {
      // silently fail
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
    try {
      reviews.value = await reviewService.getReviews(productSlug)
    } catch {
      reviews.value = []
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
