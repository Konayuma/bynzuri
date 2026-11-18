import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import VerifyEmailPage from '@/pages/auth/VerifyEmailPage.vue'
import { createPinia, setActivePinia } from 'pinia'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', name: 'home', component: { template: '<div />' } },
    { path: '/auth/login', name: 'login', component: { template: '<div />' } },
    { path: '/auth/verify-email', name: 'verify-email', component: VerifyEmailPage },
  ],
})

describe('VerifyEmailPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders loading state initially', async () => {
    await router.push({ name: 'verify-email', query: { token: 'test-token' } })
    await router.isReady()

    const wrapper = mount(VerifyEmailPage, {
      global: {
        plugins: [router],
        stubs: { BaseButton: { template: '<button><slot /></button>' } },
      },
    })
    expect(wrapper.text()).toContain('Verifying your email')
  })

  it('shows error for missing token', async () => {
    await router.push({ name: 'verify-email' })
    await router.isReady()

    const wrapper = mount(VerifyEmailPage, {
      global: {
        plugins: [router],
        stubs: { BaseButton: { template: '<button><slot /></button>' } },
      },
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Invalid verification link')
  })
})
