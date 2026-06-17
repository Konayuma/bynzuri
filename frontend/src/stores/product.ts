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
