import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import RegisterPage from '@/pages/auth/RegisterPage.vue'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'

describe('registration flow', () => {
  beforeEach(() => setActivePinia(createPinia()))

  async function setup() {
    const router = createRouter({ history: createMemoryHistory(), routes: [
      { path: '/', component: { template: '<div />' } },
      { path: '/auth/register', component: RegisterPage },
      { path: '/auth/login', component: { template: '<div />' } },
    ] })
    await router.push('/auth/register?redirect=/checkout')
    await router.isReady()
    const wrapper = mount(RegisterPage, { global: { plugins: [router] } })
    for (const [id, value] of Object.entries({ 'reg-first': 'Ada', 'reg-last': 'Test', 'reg-email': 'ada@example.com', 'reg-phone': '0971234567', 'reg-password': 'password123', 'reg-confirm': 'password123' })) {
      await wrapper.get(`#${id}`).setValue(value)
    }
    return { wrapper, router, user: useUserStore(), cart: useCartStore() }
  }

  it('sends the customer to sign in when account creation succeeded but automatic login failed', async () => {
    const { wrapper, router, user } = await setup()
    vi.spyOn(user, 'register').mockResolvedValue()
    vi.spyOn(user, 'login').mockRejectedValue(new Error('unavailable'))
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/auth/login?redirect=/checkout&created=1')
  })

  it('continues after login when cart synchronization fails', async () => {
    const { wrapper, router, user, cart } = await setup()
    vi.spyOn(user, 'register').mockResolvedValue()
    vi.spyOn(user, 'login').mockResolvedValue()
    vi.spyOn(cart, 'mergeGuestCart').mockRejectedValue(new Error('unavailable'))
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/checkout')
    expect(cart.error).toContain('Signed in')
  })
})
