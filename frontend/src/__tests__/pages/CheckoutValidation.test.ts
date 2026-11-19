import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import CheckoutPage from '@/pages/checkout/CheckoutPage.vue'
import { useCartStore } from '@/stores/cart'

vi.mock('@/services/order.service', () => ({ orderService: {
  getProvinces: vi.fn().mockResolvedValue([{ id: 'p1', name: 'Lusaka' }]),
  getTowns: vi.fn().mockResolvedValue([{ id: 't1', name: 'Lusaka' }]),
  getDeliveryMethods: vi.fn().mockResolvedValue([{ id: 'd1', name: 'Delivery', price: '10', estimated_days: '2 days' }]),
  createOrder: vi.fn(),
} }))

describe('checkout validation', () => {
  beforeEach(() => setActivePinia(createPinia()))
  it('does not advance without valid details and delivery selections', async () => {
    vi.spyOn(useCartStore(), 'fetchCart').mockResolvedValue()
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/', component: CheckoutPage }] })
    const wrapper = mount(CheckoutPage, { global: { plugins: [router] } })
    await flushPromises()
    const continueButton = () => wrapper.findAll('button').find(button => button.text().includes('Continue'))!
    await continueButton().trigger('click')
    expect(wrapper.text()).toContain('Enter your first name.')
    expect(wrapper.text()).toContain('Step 1 of 4')
    await wrapper.get('#first_name').setValue('Ada')
    await wrapper.get('#last_name').setValue('Banda')
    await wrapper.get('#email').setValue('ada@example.com')
    await wrapper.get('#phone').setValue('0971234567')
    await continueButton().trigger('click')
    expect(wrapper.text()).toContain('Step 2 of 4')
    await continueButton().trigger('click')
    expect(wrapper.text()).toContain('Select a province.')
    await wrapper.get('#province').setValue('p1')
    await flushPromises()
    await wrapper.get('#town').setValue('t1')
    await wrapper.get('#street_address').setValue('123 Main Street')
    await continueButton().trigger('click')
    expect(wrapper.text()).toContain('Step 3 of 4')
    await continueButton().trigger('click')
    expect(wrapper.text()).toContain('Select a delivery method.')
    await wrapper.get('input[name=delivery_method]').setValue()
    await continueButton().trigger('click')
    expect(wrapper.text()).toContain('Delivery details')
    expect(wrapper.text()).toContain('123 Main Street')
  })
  it('shows the actual cart subtotal and selected delivery price in the total', async () => {
    const cart = useCartStore()
    cart.cart = { id: 'cart', items: [{ id: 'line', quantity: 1, total_price: '100.00', product: { id: 'p', title: 'Oil', slug: 'oil', category: 'c', category_name: 'Care', description: '', price: '100.00', stock: 2, is_in_stock: true, images: [], rating: 0, review_count: 0, created_at: '' } }], subtotal: '100.00', total: '100.00', item_count: 1 }
    vi.spyOn(cart, 'fetchCart').mockResolvedValue()
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/', component: CheckoutPage }] })
    const wrapper = mount(CheckoutPage, { global: { plugins: [router] } })
    await flushPromises()
    const next = () => wrapper.findAll('button').find(button => button.text().includes('Continue'))!
    await wrapper.get('#first_name').setValue('Ada')
    await wrapper.get('#last_name').setValue('Banda')
    await wrapper.get('#email').setValue('ada@example.com')
    await wrapper.get('#phone').setValue('0971234567')
    await next().trigger('click')
    await wrapper.get('#province').setValue('p1')
    await flushPromises()
    await wrapper.get('#town').setValue('t1')
    await wrapper.get('#street_address').setValue('123 Main Street')
    await next().trigger('click')
    await wrapper.get('input[name=delivery_method]').setValue()
    await next().trigger('click')
    expect(wrapper.text()).toContain('K100.00')
    expect(wrapper.text()).toContain('K110.00')
    expect(wrapper.text()).not.toContain('Your cart is empty')
  })

})
