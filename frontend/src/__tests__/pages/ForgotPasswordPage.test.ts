import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
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
})
