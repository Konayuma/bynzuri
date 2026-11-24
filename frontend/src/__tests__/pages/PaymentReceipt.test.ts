import { describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import OrderConfirmationPage from '@/pages/order/OrderConfirmationPage.vue'
import { paymentService } from '@/services/payment.service'
import { orderService } from '@/services/order.service'

vi.mock('vue-router', () => ({ useRoute: () => ({ params: { id: 'order-1' } }), useRouter: () => ({ push: vi.fn() }) }))
vi.mock('@/services/order.service', () => ({ orderService: { getOrder: vi.fn().mockResolvedValue({ id: 'order-1', status: 'paid', payment_method: 'airtel_money', grand_total: '150.00', delivery_fee: '30.00', items: [{ id: 'item-1', product_title: 'Body Butter', quantity: 1, price_at_purchase: '120.00' }] }) } }))
vi.mock('@/services/payment.service', () => ({ paymentService: { getPaymentStatus: vi.fn(), initiatePayment: vi.fn() } }))

describe('payment receipt', () => {
  it.each(['pending', 'failed'])('does not issue a receipt for a %s payment', async status => {
    vi.mocked(paymentService.getPaymentStatus).mockResolvedValue({ status } as never)
    const wrapper = mount(OrderConfirmationPage)
    await flushPromises()
    expect(wrapper.find('.receipt').exists()).toBe(false)
  })
  it('shows a branded receipt after a successful payment', async () => {
    vi.mocked(paymentService.getPaymentStatus).mockResolvedValue({ status: 'success', id: 'payment-1', method: 'airtel_money', amount: '150.00', currency: 'ZMW', created_at: '2026-11-24T10:00:00Z', lenco_reference: 'ref-1' } as never)
    const wrapper = mount(OrderConfirmationPage)
    await flushPromises()
    expect(wrapper.get('.receipt').text()).toContain('ref-1')
    expect(wrapper.get('.receipt').text()).toContain('Body Butter')
    expect(wrapper.get('.receipt img').attributes('alt')).toBe('By Nzuri')
    expect(wrapper.get('.receipt-action').text()).toContain('save receipt as PDF')
  })
  it('warns when provider status cannot be verified and does not offer a retry', async () => {
    vi.mocked(orderService.getOrder).mockResolvedValue({ id: 'order-1', status: 'awaiting_payment', payment_method: 'airtel_money', grand_total: '150', items: [] } as never)
    vi.mocked(paymentService.getPaymentStatus).mockResolvedValue({ status: 'pending', verification_unavailable: true } as never)
    const wrapper = mount(OrderConfirmationPage)
    await flushPromises()
    expect(wrapper.text()).toContain('could not verify this payment')
    expect(wrapper.text()).not.toContain('Request payment')
  })
  it('blocks another request after an uncertain initiation until status is checked', async () => {
    vi.mocked(orderService.getOrder).mockResolvedValue({ id: 'order-1', status: 'awaiting_payment', payment_method: 'airtel_money', grand_total: '150', items: [] } as never)
    vi.mocked(paymentService.getPaymentStatus).mockResolvedValue({ status: 'failed' } as never)
    vi.mocked(paymentService.initiatePayment).mockRejectedValue(new Error('network'))
    const wrapper = mount(OrderConfirmationPage)
    await flushPromises()
    await wrapper.get('#retry-phone').setValue('0971234567')
    const button = wrapper.findAll('button').find(b => b.text().includes('Request payment'))!
    await button.trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('could not confirm whether the payment request was sent')
    expect(wrapper.text()).not.toContain('Request payment')
    expect(wrapper.text()).toContain('Check payment status')
  })
})
