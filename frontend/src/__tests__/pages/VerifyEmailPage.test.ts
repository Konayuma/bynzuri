import { describe, it, expect, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import VerifyEmailPage from '@/pages/auth/VerifyEmailPage.vue'
import { authService } from '@/services/auth.service'

describe('VerifyEmailPage', () => {
  async function setup() {
    const router = createRouter({ history: createMemoryHistory(), routes: [
      { path: '/auth/login', component: { template: '<div />' } },
      { path: '/auth/verify-email', component: VerifyEmailPage },
    ] })
    await router.push('/auth/verify-email?email=ada%40example.com&redirect=/checkout')
    await router.isReady()
    return { router, wrapper: mount(VerifyEmailPage, { global: { plugins: [router] } }) }
  }

  it('verifies the entered code and offers sign in', async () => {
    const { wrapper, router } = await setup()
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

  it('offers clear help for an invalid code', async () => {
    const { wrapper } = await setup()
    const verify = vi.spyOn(authService, 'verifyEmail').mockRejectedValue({ response: { status: 400 } })
    await wrapper.get('#verification-code').setValue('123456')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(wrapper.get('[role="alert"]').text()).toContain('incorrect or expired')
    expect(wrapper.text()).toContain('Send a new code')
    verify.mockRestore()
  })
})
