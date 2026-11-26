import { describe, it, expect, vi, afterEach } from 'vitest'
import { createPinia } from 'pinia'
import { flushPromises, mount } from '@vue/test-utils'
import AdminOrdersPage from '@/pages/admin/AdminOrdersPage.vue'
import { orderService } from '@/services/order.service'

vi.mock('@/layouts/AdminLayout.vue', () => ({
  default: { template: '<div><slot /></div>' },
}))

vi.mock('@/services/order.service', () => ({
  orderService: {
    getAllOrders: vi.fn(),
    updateOrderStatus: vi.fn(),
  },
}))

afterEach(() => {
  document.body.innerHTML = ''
  vi.clearAllMocks()
})

describe('AdminOrdersPage error feedback', () => {
  it('shows a dismissible alert when updating an order status fails', async () => {
    vi.mocked(orderService.getAllOrders).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 'order-12345678',
          user: 'u-1',
          user_email: 'ada@example.com',
          user_name: 'Ada Banda',
          status: 'paid',
          total_amount: '100.00',
          delivery_fee: '20.00',
          grand_total: '120.00',
          items: [],
          province: 'Lusaka',
          town: 'Lusaka',
          street_address: '123 Main',
          phone: '0971234567',
          delivery_method: 'standard',
          payment_method: 'mtn_momo',
          notes: '',
          created_at: '2026-11-20T10:00:00Z',
          updated_at: '2026-11-20T10:00:00Z',
        },
      ],
    })
    vi.mocked(orderService.updateOrderStatus).mockRejectedValue({
      response: { data: { detail: 'Invalid status transition.' } },
    })

    const wrapper = mount(AdminOrdersPage, { attachTo: document.body, global: { plugins: [createPinia()] } })
    await flushPromises()

    const actionTrigger = wrapper.get('button[aria-label="Change status for order order-12"]')
    await actionTrigger.trigger('click')
    const option = Array.from(document.body.querySelectorAll<HTMLButtonElement>('[role="option"]'))
      .find(el => el.textContent?.trim() === 'Start Processing')
    expect(option).toBeTruthy()
    option!.click()
    await flushPromises()

    const alert = wrapper.get('[role="alert"]')
    expect(alert.text()).toContain('Invalid status transition.')

    await alert.get('button').trigger('click')
    expect(wrapper.find('[role="alert"]').exists()).toBe(false)
    wrapper.unmount()
  })
})
