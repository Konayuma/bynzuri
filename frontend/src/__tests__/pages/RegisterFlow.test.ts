import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import RegisterPage from '@/pages/auth/RegisterPage.vue'
import { useUserStore } from '@/stores/user'

describe('registration flow', () => {
  beforeEach(() => setActivePinia(createPinia()))

  async function setup() {
    const router = createRouter({ history: createMemoryHistory(), routes: [
      { path: '/', component: { template: '<div />' } },
      { path: '/auth/register', component: RegisterPage },
      { path: '/auth/login', component: { template: '<div />' } },
      { path: '/auth/verify-email', component: { template: '<div />' } },
    ] })
    await router.push('/auth/register?redirect=/checkout')
    await router.isReady()
    const wrapper = mount(RegisterPage, { global: { plugins: [router] } })
    for (const [id, value] of Object.entries({ 'reg-first': 'Ada', 'reg-last': 'Test', 'reg-email': 'ada@example.com', 'reg-phone': '0971234567', 'reg-password': 'password123', 'reg-confirm': 'password123' })) {
      await wrapper.get(`#${id}`).setValue(value)
    }
    return { wrapper, router, user: useUserStore() }
  }

  it('asks the customer to verify before signing in and preserves the checkout destination', async () => {
    const { wrapper, router, user } = await setup()
    vi.spyOn(user, 'register').mockResolvedValue()
    const login = vi.spyOn(user, 'login')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(login).not.toHaveBeenCalled()
    expect(router.currentRoute.value.path).toBe('/auth/verify-email')
    expect(router.currentRoute.value.query).toEqual({ email: 'ada@example.com', redirect: '/checkout' })
  })
})
