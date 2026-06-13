import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import CartDrawer from '@/components/cart/CartDrawer.vue'
import { useCartStore } from '@/stores/cart'

function createWrapper(pinia: ReturnType<typeof createPinia>, open = true) {
  return mount(CartDrawer, {
    props: { open },
    global: {
      plugins: [pinia],
      stubs: {
        BaseDrawer: {
          template: '<div v-if="$attrs.open" class="drawer-content"><slot /></div>',
          inheritAttrs: false
        },
        BaseButton: {
          template: '<button class="btn-stub"><slot /></button>'
        },
        'router-link': true
      }
    }
  })
}

describe('CartDrawer', () => {
  it('shows empty state when cart has no items', () => {
    const pinia = createPinia()
    setActivePinia(pinia)
    const wrapper = createWrapper(pinia)
    expect(wrapper.text()).toContain('Your cart is empty')
  })

  it('shows checkout button when cart has items', () => {
    const pinia = createPinia()
    setActivePinia(pinia)
    const store = useCartStore()
    store.addToCart({
      id: 'p-1', category: 'c-1', category_name: 'Oils',
      title: 'Test Oil', slug: 'test-oil', description: '',
      price: '99.99', stock: 10, is_in_stock: true,
      images: [], rating: 4, review_count: 0,
      created_at: '2026-01-01T00:00:00Z'
    }, 2)

    const wrapper = createWrapper(pinia)
    expect(wrapper.text()).toContain('Checkout')
  })

  it('emits close event', () => {
    const pinia = createPinia()
    setActivePinia(pinia)
    const wrapper = createWrapper(pinia)
    expect(wrapper.emitted()).toBeDefined()
  })
})
