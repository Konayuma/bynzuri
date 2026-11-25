import { describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import SaleBanner from '@/components/home/SaleBanner.vue'

vi.mock('@/services/product.service', () => ({ productService: { getCampaign: vi.fn().mockResolvedValue({ title: 'Black Friday sale', percent: '30.00', starts_on: '2026-11-26', ends_on: '2026-11-28', fulfilment: 'Orders fulfilled 3rd December', enabled: true }) } }))

describe('sale banner', () => {
  it('renders the campaign details and links to the shop', async () => {
    const wrapper = mount(SaleBanner, { global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } } })
    await flushPromises()
    expect(wrapper.text()).toContain('Black Friday sale')
    expect(wrapper.text()).toContain('30% off')
    expect(wrapper.text()).toContain('26th – 28th November')
    expect(wrapper.text()).toContain('Orders fulfilled 3rd December')
  })
})
