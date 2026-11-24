import { describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import OrderHistoryPage from '@/pages/order/OrderHistoryPage.vue'
import { orderService } from '@/services/order.service'

vi.mock('@/services/order.service', () => ({ orderService: { getOrders: vi.fn() } }))

describe('order history loading', () => {
  it('shows an error and retries instead of reporting an empty history', async () => {
    vi.mocked(orderService.getOrders).mockRejectedValueOnce(new Error('network')).mockResolvedValueOnce([])
    const wrapper = mount(OrderHistoryPage)
    expect(wrapper.get('[role=status]').text()).toContain('Loading your orders')
    await flushPromises()
    expect(wrapper.get('[role=alert]').text()).toContain('couldn’t load')
    expect(wrapper.text()).not.toContain('No orders yet')
    await wrapper.findAll('button').find(button => button.text().includes('Try again'))!.trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('No orders yet')
  })
})
