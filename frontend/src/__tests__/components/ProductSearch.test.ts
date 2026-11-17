import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import ProductSearch from '@/components/search/ProductSearch.vue'
import { productService } from '@/services/product.service'

vi.mock('@/services/product.service', () => ({ productService: { getProducts: vi.fn() } }))
const router = createRouter({ history: createMemoryHistory(), routes: [
  { path: '/', component: { template: '<div />' } },
  { path: '/product/:slug', name: 'product-detail', component: { template: '<div />' } },
] })
const product = { id: '1', title: 'Growth Elixir', slug: 'growth-elixir', category_name: 'Hair Care', price: '185.00', images: [] }

beforeEach(async () => { await router.push('/'); vi.useFakeTimers(); vi.resetAllMocks() })
afterEach(() => { vi.useRealTimers() })

describe('ProductSearch', () => {
  it('shows matching products and supports keyboard selection', async () => {
    vi.mocked(productService.getProducts).mockResolvedValue({ results: [product], count: 1, next: null, previous: null } as never)
    const wrapper = mount(ProductSearch, { props: { modelValue: '' }, global: { plugins: [router] } })
    await wrapper.get('input').trigger('focus')
    await wrapper.setProps({ modelValue: 'grow' })
    expect(wrapper.text()).toContain('Searching products')
    await vi.advanceTimersByTimeAsync(250)
    await flushPromises()
    expect(productService.getProducts).toHaveBeenCalledWith({ search: 'grow' })
    expect(wrapper.text()).toContain('Growth Elixir')
    await wrapper.get('input').trigger('keydown', { key: 'ArrowDown' })
    expect(wrapper.get('[role="option"]').attributes('aria-selected')).toBe('true')
    await wrapper.get('input').trigger('keydown', { key: 'Enter' })
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/product/growth-elixir')
    wrapper.unmount()
  })

  it('ignores older responses and shows an empty result', async () => {
    let resolveOld!: (value: never) => void
    vi.mocked(productService.getProducts).mockImplementationOnce(() => new Promise(resolve => { resolveOld = resolve })).mockResolvedValueOnce({ results: [], count: 0, next: null, previous: null } as never)
    const wrapper = mount(ProductSearch, { props: { modelValue: '' }, global: { plugins: [router] } })
    await wrapper.get('input').trigger('focus')
    await wrapper.setProps({ modelValue: 'old' })
    await vi.advanceTimersByTimeAsync(250)
    await wrapper.setProps({ modelValue: 'new' })
    await vi.advanceTimersByTimeAsync(250)
    resolveOld({ results: [product] } as never)
    await flushPromises()
    expect(wrapper.text()).toContain('No products found')
    expect(wrapper.text()).not.toContain('Growth Elixir')
    wrapper.unmount()
  })

  it('shows a useful error when search fails', async () => {
    vi.mocked(productService.getProducts).mockRejectedValue(new Error('offline'))
    const wrapper = mount(ProductSearch, { props: { modelValue: '' }, global: { plugins: [router] } })
    await wrapper.get('input').trigger('focus')
    await wrapper.setProps({ modelValue: 'oil' })
    await vi.advanceTimersByTimeAsync(250)
    await flushPromises()
    expect(wrapper.text()).toContain('Search is unavailable')
    wrapper.unmount()
  })
})
