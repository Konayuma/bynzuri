import { describe, it, expect, beforeEach } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import LoginPage from '@/pages/auth/LoginPage.vue'
import { createPinia, setActivePinia } from 'pinia'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', name: 'home', component: { template: '<div />' } },
    { path: '/auth/login', name: 'login', component: LoginPage },
    { path: '/auth/register', name: 'register', component: { template: '<div />' } },
    { path: '/auth/forgot-password', name: 'forgot-password', component: { template: '<div />' } },
  ],
})

describe('LoginPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders login form', () => {
    const wrapper = mount(LoginPage, {
      global: {
        plugins: [router],
        stubs: { BaseButton: { template: '<button><slot /></button>' }, BaseInput: { template: '<input />' } },
      },
    })
    expect(wrapper.text()).toContain('Welcome Back')
    expect(wrapper.text()).toContain('Sign In')
  })

  it('shows error when submitting empty form', async () => {
    const wrapper = mount(LoginPage, {
      global: {
        plugins: [router],
        stubs: { BaseButton: { template: '<button><slot /></button>' }, BaseInput: { template: '<input />' } },
      },
    })
    await wrapper.find('form').trigger('submit')
    expect(wrapper.text()).toContain('Enter both your email and password')
  })

  it('has link to register page', () => {
    const wrapper = mount(LoginPage, {
      global: {
        plugins: [router],
        stubs: { BaseButton: { template: '<button><slot /></button>' }, BaseInput: { template: '<input />' } },
      },
    })
    const links = wrapper.findAll('a')
    const registerLink = links.find((l) => l.text().includes('Create one'))
    expect(registerLink).toBeDefined()
  })

  it('has link to forgot password page', () => {
    const wrapper = mount(LoginPage, {
      global: {
        plugins: [router],
        stubs: { BaseButton: { template: '<button><slot /></button>' }, BaseInput: { template: '<input />' } },
      },
    })
    const links = wrapper.findAll('a')
    const forgotLink = links.find((l) => l.text().includes('Forgot password'))
    expect(forgotLink).toBeDefined()
  })

  it('suggests resetting password when redirected from an existing account signup', async () => {
    await router.push('/auth/login?reason=exists')
    await router.isReady()
    const wrapper = mount(LoginPage, {
      global: {
        plugins: [router],
        stubs: { BaseButton: { template: '<button><slot /></button>' }, BaseInput: { template: '<input />' } },
      },
    })
    expect(wrapper.text()).toContain('already have an account')
    const resetButton = wrapper.findAll('button').find((b) => b.text().includes('Reset your password'))
    expect(resetButton).toBeDefined()
    await resetButton!.trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/auth/forgot-password')
  })
})
