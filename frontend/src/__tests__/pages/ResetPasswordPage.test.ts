import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory, useRoute } from 'vue-router'
import ResetPasswordPage from '@/pages/auth/ResetPasswordPage.vue'
import { createPinia, setActivePinia } from 'pinia'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', name: 'home', component: { template: '<div />' } },
    { path: '/auth/login', name: 'login', component: { template: '<div />' } },
    { path: '/auth/reset-password', name: 'reset-password', component: ResetPasswordPage },
  ],
})

describe('ResetPasswordPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders reset password form', async () => {
    router.push({ name: 'reset-password', query: { uid: 'test', token: 'test' } })
    await router.isReady()

    const wrapper = mount(ResetPasswordPage, {
      global: {
        plugins: [router],
        stubs: { BaseButton: { template: '<button><slot /></button>' }, BaseInput: { template: '<input />' } },
      },
    })
    expect(wrapper.text()).toContain('New Password')
    expect(wrapper.text()).toContain('Reset Password')
  })

  it('shows error when passwords do not match', async () => {
    router.push({ name: 'reset-password', query: { uid: 'test', token: 'test' } })
    await router.isReady()

    const wrapper = mount(ResetPasswordPage, {
      global: {
        plugins: [router],
        stubs: { BaseButton: { template: '<button><slot /></button>' }, BaseInput: { template: '<input />' } },
      },
    })
    await wrapper.find('form').trigger('submit')
    expect(wrapper.text()).toContain('Enter both password fields')
  })

  it('shows error for invalid reset link', async () => {
    router.push({ name: 'reset-password' })
    await router.isReady()

    const wrapper = mount(ResetPasswordPage, {
      global: {
        plugins: [router],
        stubs: { BaseButton: { template: '<button><slot /></button>' }, BaseInput: { template: '<input />' } },
      },
    })
    expect(wrapper.text()).toContain('Invalid reset link')
  })
})
