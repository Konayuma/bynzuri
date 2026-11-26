import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import AccountPage from '@/pages/account/AccountPage.vue'
import { useUserStore } from '@/stores/user'
import { useUIStore } from '@/stores/ui'
import { addressService } from '@/services/address.service'
import { orderService } from '@/services/order.service'

vi.mock('@/services/address.service', () => ({
  addressService: {
    getAddresses: vi.fn(),
    createAddress: vi.fn(),
    updateAddress: vi.fn(),
    deleteAddress: vi.fn(),
  }
}))

vi.mock('@/services/order.service', () => ({
  orderService: {
    getProvinces: vi.fn(),
    getTowns: vi.fn(),
    getOrders: vi.fn(),
  }
}))

async function mountAccount() {
  const pinia = createPinia()
  setActivePinia(pinia)
  const userStore = useUserStore()
  userStore.user = {
    id: 'u-1',
    email: 'monica@example.com',
    first_name: 'Monica',
    last_name: 'Banda',
    phone: '+260971234567',
    role: 'customer',
    email_verified: true,
  }
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/account', component: AccountPage },
      { path: '/account/orders', component: { template: '<div />' } },
      { path: '/wishlist', component: { template: '<div />' } },
      { path: '/help', component: { template: '<div />' } },
      { path: '/auth/forgot-password', component: { template: '<div />' } },
      { path: '/catalog', component: { template: '<div />' } },
      { path: '/', component: { template: '<div />' } },
    ],
  })
  await router.push('/account')
  await router.isReady()
  const wrapper = mount(AccountPage, { global: { plugins: [pinia, router] } })
  await flushPromises()
  return { wrapper, userStore }
}

describe('AccountPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(addressService.getAddresses).mockResolvedValue([])
    vi.mocked(orderService.getProvinces).mockResolvedValue([{ id: 'p-1', name: 'Lusaka' }])
    vi.mocked(orderService.getOrders).mockResolvedValue([])
  })

  it('renders profile details, verified badge, recent orders, and security links', async () => {
    const { wrapper } = await mountAccount()
    expect(wrapper.text()).toContain('Welcome, Monica')
    expect(wrapper.text()).toContain('MB')
    expect(wrapper.text()).toContain('Verified email')
    expect(wrapper.text()).toContain('monica@example.com')
    expect(wrapper.text()).toContain('+260971234567')
    expect(wrapper.text()).toContain('Recent Orders')
    expect(wrapper.text()).toContain('Saved Addresses')
    expect(wrapper.text()).toContain('Reset Password')
    expect(wrapper.text()).toContain('Help & Returns')
  })

  it('allows editing personal details and validates Zambian phone format', async () => {
    const { wrapper, userStore } = await mountAccount()
    const uiStore = useUIStore()
    const updateSpy = vi.spyOn(userStore, 'updateProfile').mockImplementation(async (patch) => {
      userStore.user = { ...userStore.user!, ...patch }
    })

    const editBtn = wrapper.findAll('button').find(b => b.text().trim() === 'Edit')!
    await editBtn.trigger('click')
    await wrapper.get('#profile-phone').setValue('12345')
    await wrapper.get('form').trigger('submit')
    expect(wrapper.get('[role=alert]').text()).toContain('valid phone number')
    expect(updateSpy).not.toHaveBeenCalled()

    await wrapper.get('#profile-first-name').setValue('Mona')
    await wrapper.get('#profile-phone').setValue('0977654321')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(updateSpy).toHaveBeenCalledWith({
      first_name: 'Mona',
      last_name: 'Banda',
      phone: '0977654321',
    })
    expect(uiStore.toast?.message).toContain('Profile details updated')
  })

  it('stays rendered cleanly even if orders, addresses, or provinces fail', async () => {
    vi.mocked(addressService.getAddresses).mockRejectedValueOnce(new Error('offline'))
    vi.mocked(orderService.getProvinces).mockRejectedValueOnce(new Error('offline'))
    vi.mocked(orderService.getOrders).mockRejectedValueOnce(new Error('offline'))

    const { wrapper } = await mountAccount()
    expect(wrapper.text()).toContain('Welcome, Monica')
    expect(wrapper.text()).toContain('Could not load your recent orders.')
    expect(wrapper.text()).toContain('Could not load your saved addresses.')
  })
})
