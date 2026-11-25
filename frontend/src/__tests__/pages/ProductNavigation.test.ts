import { describe, expect, it, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import ProductDetailPage from '@/pages/product/ProductDetailPage.vue'
import { productService } from '@/services/product.service'

vi.mock('@/services/product.service', () => ({ productService: {
  getProduct: vi.fn(async (slug: string) => ({ id: slug, slug, title: slug === 'one' ? 'First product' : 'Second product', category_name: 'Hair Care', category_slug: 'hair-care', price: '100', stock: 0, is_in_stock: false, images: [], rating: 0, review_count: 0 })),
  getProducts: vi.fn(async () => ({ results: [], count: 0, next: null, previous: null })),
} }))
vi.mock('@/services/review.service', () => ({ reviewService: { getReviews: vi.fn(async () => []) } }))

describe('product search navigation', () => {
  it('lets a customer increase and decrease quantity within stock', async () => {
    vi.mocked(productService.getProduct).mockResolvedValueOnce({ id: 'one', slug: 'one', title: 'Serum', category: 'hair', category_name: 'Hair', description: 'A serum.\n\n- Gentle', price: '100', stock: 5, is_in_stock: true, images: [], rating: 0, review_count: 0, created_at: '' })
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/product/:slug', component: ProductDetailPage }] })
    await router.push('/product/one')
    await router.isReady()
    const wrapper = mount({ template: '<router-view />' }, { global: { plugins: [createPinia(), router] } })
    await flushPromises()
    const group = wrapper.get('[role="group"][aria-label="Quantity"]')
    const purchase = wrapper.findAll('button').find(button => button.text().includes('Add to Cart'))!
    const details = wrapper.get('section[aria-label="Product details"]')
    expect(purchase.element.compareDocumentPosition(details.element) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    await group.get('[aria-label="Increase quantity"]').trigger('click')
    expect(group.text()).toContain('2')
    await group.get('[aria-label="Decrease quantity"]').trigger('click')
    expect(group.text()).toContain('1')
    expect(wrapper.get('ul li').text()).toBe('Gentle')
    wrapper.unmount()
  })
  it('loads the newly selected product when navigating between detail pages', async () => {
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/product/:slug', component: ProductDetailPage }] })
    await router.push('/product/one')
    await router.isReady()
    const wrapper = mount({ template: '<router-view />' }, { global: { plugins: [createPinia(), router] } })
    await flushPromises()
    expect(wrapper.text()).toContain('First product')
    await router.push('/product/two')
    await flushPromises()
    expect(wrapper.text()).toContain('Second product')
    expect(wrapper.find('h1').text()).not.toContain('First product')
    wrapper.unmount()
  })
})
