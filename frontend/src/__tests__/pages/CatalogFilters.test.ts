import { describe, it, expect, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import CatalogPage from '@/pages/catalog/CatalogPage.vue'
import { productService } from '@/services/product.service'

vi.mock('@/services/product.service', () => ({ productService: {
  getProducts: vi.fn(async () => ({ results: [], count: 0, next: null, previous: null })),
  getCategories: vi.fn(async () => [{ id: '1', name: 'Hair Care', slug: 'hair-care', product_count: 4 }]),
} }))

async function setup(query = '') {
  const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/catalog', component: CatalogPage }] })
  await router.push(`/catalog${query}`)
  await router.isReady()
  const wrapper = mount(CatalogPage, { global: { plugins: [createPinia(), router] } })
  await flushPromises()
  return { wrapper, router }
}

describe('catalog filters', () => {
  it('combines filters with search, resets pagination, and removes filters independently', async () => {
    const { wrapper, router } = await setup('?search=oil&page=2')
    await wrapper.findAll('input[type=radio]')[1]!.setValue()
    await flushPromises()
    expect(router.currentRoute.value.query).toMatchObject({ search: 'oil', category: 'hair-care' })
    expect(router.currentRoute.value.query.page).toBeUndefined()
    const priceInputs = wrapper.findAll('input[inputmode=decimal]')
    await priceInputs[0]!.setValue('50')
    await priceInputs[1]!.setValue('200')
    await wrapper.findAll('button').find(b => b.text() === 'Apply price')!.trigger('click')
    await flushPromises()
    await wrapper.get('input[type=checkbox]').setValue(true)
    await flushPromises()
    expect(router.currentRoute.value.query).toMatchObject({ search: 'oil', category: 'hair-care', min_price: '50', max_price: '200', in_stock: 'true' })
    expect(productService.getProducts).toHaveBeenLastCalledWith(expect.objectContaining({ search: 'oil', category: 'hair-care', min_price: '50', max_price: '200', in_stock: true }))
    await wrapper.get('[aria-label="Remove price filter"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.query.min_price).toBeUndefined()
    expect(router.currentRoute.value.query.category).toBe('hair-care')
    expect(router.currentRoute.value.query.search).toBe('oil')
    wrapper.unmount()
  })

  it('opens and closes the mobile filter panel and returns focus', async () => {
    const { wrapper } = await setup()
    const toggle = wrapper.get('button[aria-controls="catalog-filters"]')
    expect(toggle.attributes('aria-expanded')).toBe('false')
    await toggle.trigger('click')
    expect(toggle.attributes('aria-expanded')).toBe('true')
    expect(wrapper.get('#catalog-filters').classes()).toContain('block')
    await wrapper.findAll('button').find(b => b.text() === 'Show products')!.trigger('click')
    expect(toggle.attributes('aria-expanded')).toBe('false')
    wrapper.unmount()
  })

  it('prevents an invalid price range and restores URL filters', async () => {
    const { wrapper, router } = await setup('?min_price=100&in_stock=true')
    const priceInputs = wrapper.findAll('input[inputmode=decimal]')
    expect((priceInputs[0]!.element as HTMLInputElement).value).toBe('100')
    expect((wrapper.get('input[type=checkbox]').element as HTMLInputElement).checked).toBe(true)
    await priceInputs[1]!.setValue('50')
    await wrapper.findAll('button').find(b => b.text() === 'Apply price')!.trigger('click')
    expect(wrapper.get('[role=alert]').text()).toContain('Minimum price')
    expect(router.currentRoute.value.query.max_price).toBeUndefined()
    wrapper.unmount()
  })
})
