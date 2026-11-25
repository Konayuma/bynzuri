import { describe, it, expect, vi, beforeEach } from 'vitest'
import { flushPromises, mount, RouterLinkStub } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ProductCard from '@/components/product/ProductCard.vue'
import { useCartStore } from '@/stores/cart'
import { useWishlistStore } from '@/stores/wishlist'
import { useUIStore } from '@/stores/ui'

const pushMock = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: pushMock })
}))

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
      stubs: { RouterLink: RouterLinkStub }
    }
  })
}

describe('ProductCard', () => {
  beforeEach(() => {
    pushMock.mockReset()
    localStorage.clear()
  })

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

  it('keeps action buttons off the product image container', () => {
    const wrapper = createWrapper()
    const imageContainer = wrapper.get('div.aspect-\\[3\\/4\\]')
    expect(imageContainer.findAll('button')).toHaveLength(0)
  })

  it('shows out of stock overlay and disables Add to Cart when stock is 0', () => {
    const outOfStock = { ...mockProduct, stock: 0, is_in_stock: false }
    const wrapper = createWrapper(outOfStock)
    expect(wrapper.text()).toContain('Out of Stock')
    const outBtn = wrapper.findAll('button').find(b => b.text().includes('Out of Stock'))
    expect(outBtn?.attributes('disabled')).toBeDefined()
  })

  it('renders product image when available', () => {
    const wrapper = createWrapper()
    const img = wrapper.find('img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe('/test.jpg')
  })

  it('keeps a placeholder until the product image loads', async () => {
    const wrapper = createWrapper()
    expect(wrapper.get('img').classes()).toContain('opacity-0')
    await wrapper.get('img').trigger('load')
    expect(wrapper.get('img').classes()).not.toContain('opacity-0')
  })

  it('renders image placeholder when no images', () => {
    const noImg = { ...mockProduct, images: [] }
    const wrapper = createWrapper(noImg)
    const img = wrapper.find('img')
    expect(img.exists()).toBe(false)
  })

  it('adds product to cart and triggers bag toast on Add to Cart click', async () => {
    const wrapper = createWrapper()
    const cartStore = useCartStore()
    const uiStore = useUIStore()
    const addBtn = wrapper.findAll('button').find(b => b.text().includes('Add to Cart'))!
    await addBtn.trigger('click')
    await flushPromises()
    expect(cartStore.itemCount).toBe(1)
    expect(wrapper.text()).toContain('Added to Cart')
    expect(uiStore.toast?.message).toContain('Growth Oil')
  })

  it('toggles wishlist state from the metadata row heart button', async () => {
    const wrapper = createWrapper()
    const wishlistStore = useWishlistStore()
    const favBtn = wrapper.get('button[aria-label="Add to wishlist"]')
    await favBtn.trigger('click')
    expect(wishlistStore.isWishlisted(mockProduct.id)).toBe(true)
    expect(wrapper.find('button[aria-label="Remove from wishlist"]').exists()).toBe(true)
  })
})
