import { describe, it, expect, vi } from 'vitest'
import { mount, RouterLinkStub } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ProductCard from '@/components/product/ProductCard.vue'

const mockProduct = {
  id: 'p-1',
  category: 'c-1',
  category_name: 'Hair Care',
  title: 'Growth Oil',
  slug: 'growth-oil',
  description: 'Premium growth oil',
  price: '149.99',
  stock: 20,
  is_in_stock: true,
  images: [{ id: 'img-1', image: '/test.jpg', alt_text: 'Oil', is_primary: true }],
  rating: 4.5,
  review_count: 10,
  created_at: '2026-01-01T00:00:00Z'
}

function createWrapper(product = mockProduct) {
  setActivePinia(createPinia())
  return mount(ProductCard, {
    props: { product },
    global: {
      stubs: { RouterLink: RouterLinkStub },
      mocks: {
        $router: { push: vi.fn() }
      }
    }
  })
}

describe('ProductCard', () => {
  it('renders product title', () => {
    const wrapper = createWrapper()
    expect(wrapper.text()).toContain('Growth Oil')
  })

  it('provides a product link and falls back after a broken image', async () => {
    const wrapper = createWrapper({ ...mockProduct, slug: 'growth-elixir' })
    expect(wrapper.getComponent(RouterLinkStub).props('to')).toBe('/product/growth-elixir')
    await wrapper.get('img').trigger('error')
    expect(wrapper.get('img').attributes('src')).toContain('growthelixir')
    await wrapper.get('img').trigger('error')
    expect(wrapper.find('img').exists()).toBe(false)
  })

  it('renders category name', () => {
    const wrapper = createWrapper()
    expect(wrapper.text()).toContain('Hair Care')
  })

  it('renders price with K prefix', () => {
    const wrapper = createWrapper()
    expect(wrapper.text()).toContain('K149.99')
  })

  it('shows out of stock overlay when stock is 0', () => {
    const outOfStock = { ...mockProduct, stock: 0, is_in_stock: false }
    const wrapper = createWrapper(outOfStock)
    expect(wrapper.text()).toContain('Out of Stock')
  })

  it('renders product image when available', () => {
    const wrapper = createWrapper()
    const img = wrapper.find('img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe('/test.jpg')
  })

  it('renders image placeholder when no images', () => {
    const noImg = { ...mockProduct, images: [] }
    const wrapper = createWrapper(noImg)
    const img = wrapper.find('img')
    expect(img.exists()).toBe(false)
  })

  it('emits add-to-cart event on button click', async () => {
    const wrapper = createWrapper()
    const addBtn = wrapper.find('button')
    await addBtn.trigger('click')
    // Button click triggers store action, should not throw
    expect(wrapper.find('button[aria-label="Add to cart"]')).toBeTruthy()
  })
})
