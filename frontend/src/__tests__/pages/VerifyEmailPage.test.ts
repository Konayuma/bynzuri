import { beforeEach, describe, it, expect, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import VerifyEmailPage from '@/pages/auth/VerifyEmailPage.vue'
import { authService } from '@/services/auth.service'
import { clearSignupCredentials, rememberSignupCredentials, rememberVerificationEmail, takeSignupCredentials } from '@/services/verification-context'
import { createPinia, setActivePinia } from 'pinia'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'

describe('VerifyEmailPage', () => {
  beforeEach(() => { clearSignupCredentials(); setActivePinia(createPinia()) })
  async function setup() {
    const router = createRouter({ history: createMemoryHistory(), routes: [
      { path: '/auth/login', component: { template: '<div />' } },
      { path: '/auth/verify-email', component: VerifyEmailPage },
      { path: '/checkout', component: { template: '<div />' } },
      { path: '/', component: { template: '<div />' } },
    ] })
    await router.push('/auth/verify-email?email=ada%40example.com&redirect=/checkout')
    await router.isReady()
    return { router, wrapper: mount(VerifyEmailPage, { global: { plugins: [router] } }) }
  }

  it('signs in after verification and returns the customer to checkout', async () => {
    rememberSignupCredentials('ada@example.com', 'password123')
    const { wrapper, router } = await setup()
    const verify = vi.spyOn(authService, 'verifyEmail').mockResolvedValue()
    const login = vi.spyOn(useUserStore(), 'login').mockResolvedValue()
    const merge = vi.spyOn(useCartStore(), 'mergeGuestCart').mockResolvedValue()
    const cart = vi.spyOn(useCartStore(), 'fetchCart').mockResolvedValue()
    await wrapper.get('#verification-code').setValue('123456')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(login).toHaveBeenCalledWith('ada@example.com', 'password123')
    expect(merge).toHaveBeenCalledOnce()
    expect(cart).toHaveBeenCalledOnce()
    expect(router.currentRoute.value.path).toBe('/checkout')
    expect(takeSignupCredentials('ada@example.com')).toBeNull()
    verify.mockRestore(); login.mockRestore(); merge.mockRestore(); cart.mockRestore()
  })

  it('keeps verification complete and offers sign-in if automatic login fails', async () => {
    rememberSignupCredentials('ada@example.com', 'password123')
    const { wrapper } = await setup()
    const verify = vi.spyOn(authService, 'verifyEmail').mockResolvedValue()
    const login = vi.spyOn(useUserStore(), 'login').mockRejectedValue(new Error('offline'))
    await wrapper.get('#verification-code').setValue('123456')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(wrapper.text()).toContain('Email verified')
    expect(wrapper.text()).toContain('Continue to sign in')
    expect(takeSignupCredentials('ada@example.com')).toBeNull()
    verify.mockRestore(); login.mockRestore()
  })

  it('continues when sign-in succeeds but guest cart restoration fails', async () => {
    rememberSignupCredentials('ada@example.com', 'password123')
    const { wrapper, router } = await setup()
    const verify = vi.spyOn(authService, 'verifyEmail').mockResolvedValue()
    const login = vi.spyOn(useUserStore(), 'login').mockResolvedValue()
    const cart = useCartStore()
    const merge = vi.spyOn(cart, 'mergeGuestCart').mockRejectedValue(new Error('offline'))
    await wrapper.get('#verification-code').setValue('123456')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/checkout')
    expect(cart.error).toContain('cart could not be restored')
    verify.mockRestore(); login.mockRestore(); merge.mockRestore()
  })

  it('does not use sign-up credentials for a different account', async () => {
    rememberSignupCredentials('someone-else@example.com', 'password123')
    const { wrapper } = await setup()
    const verify = vi.spyOn(authService, 'verifyEmail').mockResolvedValue()
    const login = vi.spyOn(useUserStore(), 'login').mockResolvedValue()
    await wrapper.get('#verification-code').setValue('123456')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(login).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('Continue to sign in')
    verify.mockRestore(); login.mockRestore()
  })

  it('verifies the entered code and offers sign in', async () => {
    const { wrapper, router } = await setup()
    await flushPromises()
    expect(wrapper.find('#verification-email').exists()).toBe(false)
    expect(router.currentRoute.value.query.email).toBeUndefined()
    const verify = vi.spyOn(authService, 'verifyEmail').mockResolvedValue()
    await wrapper.get('#verification-code').setValue('123456')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(verify).toHaveBeenCalledWith('ada@example.com', '123456')
    expect(wrapper.text()).toContain('Email verified')
    await wrapper.get('button').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.query.redirect).toBe('/checkout')
    verify.mockRestore()
  })

  it('allows a returning customer to enter an email if the sign-up context is missing', async () => {
    rememberVerificationEmail('')
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/auth/verify-email', component: VerifyEmailPage }] })
    await router.push('/auth/verify-email')
    await router.isReady()
    const wrapper = mount(VerifyEmailPage, { global: { plugins: [router] } })
    expect(wrapper.find('#verification-email').exists()).toBe(true)
    expect(wrapper.text()).toContain('Use the email address you signed up with')
  })

  it('offers clear help for an invalid code', async () => {
    const { wrapper } = await setup()
    const verify = vi.spyOn(authService, 'verifyEmail').mockRejectedValue({ response: { status: 400 } })
    await wrapper.get('#verification-code').setValue('123456')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(wrapper.get('[role="alert"]').text()).toContain('incorrect or has expired')
    expect(wrapper.text()).toContain('Send a new code')
    verify.mockRestore()
  })

  it('requests a new code for the saved account without rendering an email input', async () => {
    const { wrapper } = await setup()
    const resend = vi.spyOn(authService, 'resendVerificationEmail').mockResolvedValue()
    expect(wrapper.text()).toContain('ada@example.com')
    const button = wrapper.findAll('button').find(item => item.text() === 'Send a new code')!
    await button.trigger('click')
    await flushPromises()
    expect(resend).toHaveBeenCalledWith('ada@example.com')
    expect(wrapper.text()).toContain('check your spam folder')
    expect(wrapper.find('#verification-email').exists()).toBe(false)
    resend.mockRestore()
  })

  it('offers sign-in recovery after a lost verification response without claiming success', async () => {
    const { wrapper, router } = await setup()
    const verify = vi.spyOn(authService, 'verifyEmail').mockRejectedValue(new Error('offline'))
    await wrapper.get('#verification-code').setValue('123456')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(wrapper.get('[role="alert"]').text()).toContain('could not verify')
    const signIn = wrapper.findAll('button').find(item => item.text() === 'Continue to sign in')!
    await signIn.trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/auth/login')
    expect(router.currentRoute.value.query.verified).toBeUndefined()
    verify.mockRestore()
  })
})
