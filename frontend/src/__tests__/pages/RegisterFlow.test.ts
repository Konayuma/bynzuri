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
    const register = vi.spyOn(user, 'register').mockResolvedValue()
    const login = vi.spyOn(user, 'login')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(login).not.toHaveBeenCalled()
    expect(register).toHaveBeenCalledWith(expect.objectContaining({ phone: '+260971234567' }))
    expect(router.currentRoute.value.path).toBe('/auth/verify-email')
    expect(router.currentRoute.value.query).toEqual({ redirect: '/checkout' })
    expect(sessionStorage.getItem('bynzuri_verification_email')).toBe('ada@example.com')
  })

  it('accepts another country and sends an international number', async () => {
    const { wrapper, user } = await setup()
    const register = vi.spyOn(user, 'register').mockResolvedValue()
    await wrapper.get('select[aria-label="Phone country code"]').setValue('US')
    await wrapper.get('#reg-phone').setValue('2025550123')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(register).toHaveBeenCalledWith(expect.objectContaining({ phone: '+12025550123' }))
  })

  it('rejects an invalid number for the chosen country', async () => {
    const { wrapper, user } = await setup()
    const register = vi.spyOn(user, 'register').mockResolvedValue()
    await wrapper.get('#reg-phone').setValue('123')
    await wrapper.get('form').trigger('submit')
    expect(wrapper.text()).toContain('Enter a valid number for the selected country.')
    expect(register).not.toHaveBeenCalled()
  })

  it('does not show a continue verification link on account creation', async () => {
    const { wrapper } = await setup()
    expect(wrapper.text()).not.toContain('Continue verification')
  })

  it('collapses pasted or autofilled full numbers with calling code', async () => {
    const { wrapper, user } = await setup()
    const register = vi.spyOn(user, 'register').mockResolvedValue()
    const phoneInput = wrapper.get('#reg-phone')

    await phoneInput.setValue('260978734029')
    expect((phoneInput.element as HTMLInputElement).value).toBe('978734029')

    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(register).toHaveBeenCalledWith(expect.objectContaining({ phone: '+260978734029' }))
  })

  it('auto-switches country and collapses when pasting a foreign international number', async () => {
    const { wrapper, user } = await setup()
    const register = vi.spyOn(user, 'register').mockResolvedValue()
    const phoneInput = wrapper.get('#reg-phone')

    await phoneInput.setValue('+1 202 555 0123')
    expect((phoneInput.element as HTMLInputElement).value).toBe('2025550123')
    expect((wrapper.get('select[aria-label="Phone country code"]').element as HTMLSelectElement).value).toBe('US')

    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(register).toHaveBeenCalledWith(expect.objectContaining({ phone: '+12025550123' }))
  })
})
