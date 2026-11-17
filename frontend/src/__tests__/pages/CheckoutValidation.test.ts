import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import CheckoutPage from '@/pages/checkout/CheckoutPage.vue'

vi.mock('@/services/order.service', () => ({ orderService: {
  getProvinces: vi.fn().mockResolvedValue([{ id: 'p1', name: 'Lusaka' }]),
  getTowns: vi.fn().mockResolvedValue([{ id: 't1', name: 'Lusaka' }]),
  getDeliveryMethods: vi.fn().mockResolvedValue([{ id: 'd1', name: 'Delivery', price: '10', estimated_days: '2 days' }]),
  createOrder: vi.fn(),
} }))

describe('checkout validation', () => {
  beforeEach(() => setActivePinia(createPinia()))
  it('does not advance without valid details and delivery selections', async () => {
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
})
