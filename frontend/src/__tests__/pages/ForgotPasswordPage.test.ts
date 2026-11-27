import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { authService } from '@/services/auth.service'
import { createRouter, createMemoryHistory } from 'vue-router'
import ForgotPasswordPage from '@/pages/auth/ForgotPasswordPage.vue'
import { createPinia, setActivePinia } from 'pinia'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', name: 'home', component: { template: '<div />' } },
    { path: '/auth/login', name: 'login', component: { template: '<div />' } },
    { path: '/auth/forgot-password', name: 'forgot-password', component: ForgotPasswordPage },
  ],
})

describe('ForgotPasswordPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders forgot password form', () => {
    const wrapper = mount(ForgotPasswordPage, {
      global: {
        plugins: [router],
        stubs: { BaseButton: { template: '<button><slot /></button>' }, BaseInput: { template: '<input />' } },
      },
    })
    expect(wrapper.text()).toContain('Reset Password')
    expect(wrapper.text()).toContain('Send Reset Link')
  })

  it('shows error when submitting empty form', async () => {
    const wrapper = mount(ForgotPasswordPage, {
      global: {
        plugins: [router],
        stubs: { BaseButton: { template: '<button><slot /></button>' }, BaseInput: { template: '<input />' } },
      },
    })
    await wrapper.find('form').trigger('submit')
    expect(wrapper.text()).toContain('Enter your email address')
  })

  it('has link back to login', () => {
    const wrapper = mount(ForgotPasswordPage, {
      global: {
        plugins: [router],
        stubs: { BaseButton: { template: '<button><slot /></button>' }, BaseInput: { template: '<input />' } },
      },
    })
    expect(wrapper.text()).toContain('Sign in')
  })

  it('explains Google sign-in and keeps the response neutral after a reset request', async () => {
    const request = vi.spyOn(authService, 'forgotPassword').mockResolvedValueOnce()
    const wrapper = mount(ForgotPasswordPage, { global: { plugins: [router] } })
    expect(wrapper.text()).toContain('This won’t change your Google password')
    expect(wrapper.find('a[href="https://accounts.google.com/signin/recovery"]').exists()).toBe(true)
    await wrapper.find('input').setValue('person@example.com')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(request).toHaveBeenCalledWith('person@example.com', window.location.origin)
    expect(wrapper.text()).toContain('If an active account exists')
    expect(wrapper.text()).toContain('Used Google to sign in?')
    request.mockRestore()
  })
})
