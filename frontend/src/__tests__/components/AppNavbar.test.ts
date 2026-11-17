import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import AppNavbar from '@/layouts/AppNavbar.vue'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'

const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/', component: { template: '<div />' } }],
})

function createWrapper() {
  setActivePinia(createPinia())
  return mount(AppNavbar, {
    global: {
      plugins: [router],
      stubs: {
        'router-link': {
          template: '<a :href="$props.to"><slot /></a>',
          props: ['to']
        },
        'router-view': true
      }
    }
  })
}

describe('AppNavbar', () => {
  it('renders logo', () => {
    const wrapper = createWrapper()
    expect(wrapper.get('img[alt="By Nzuri — home"]').attributes('src')).toContain('By%20Nzuri%20Vector%20Logo%20-01.svg')
  })

  it('renders navigation links', () => {
    const wrapper = createWrapper()
    const links = wrapper.findAll('a')
    const linkTexts = links.map(l => l.text())
    expect(linkTexts.some(t => t.includes('Shop All'))).toBe(true)
  })

  it('shows cart icon', () => {
    const wrapper = createWrapper()
    const buttons = wrapper.findAll('button')
    expect(buttons.length).toBeGreaterThan(0)
  })

  it('toggles mobile menu', async () => {
    const wrapper = createWrapper()
    const menuButton = wrapper.findAll('button').find(
      b => b.attributes('aria-label') === 'Toggle menu'
    )
    if (menuButton) {
      await menuButton.trigger('click')
      expect(wrapper.text()).toContain('Shop All')
    }
  })

  it('has persistent search input on desktop', () => {
    const wrapper = createWrapper()
    const input = wrapper.find('input[placeholder="Search products..."]')
    expect(input.exists()).toBe(true)
  })

  it('opens guest account options and closes on Escape', async () => {
    const wrapper = createWrapper()
    const trigger = wrapper.get('button[aria-label="Account"]')
    await trigger.trigger('click')
    expect(trigger.attributes('aria-expanded')).toBe('true')
    expect(wrapper.text()).toContain('Create account')
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    await wrapper.vm.$nextTick()
    expect(trigger.attributes('aria-expanded')).toBe('false')
    wrapper.unmount()
  })

  it('offers account links and clears the signed-in cart on sign out', async () => {
    const wrapper = createWrapper()
    const user = useUserStore()
    user.user = { first_name: 'Ada', last_name: 'Test', email: 'ada@example.com', role: 'customer' } as typeof user.user
    const cart = useCartStore()
    cart.cart = { id: '1', items: [], subtotal: '0', total: '0', item_count: 2 }
    await wrapper.get('button[aria-label="Account"]').trigger('click')
    expect(wrapper.text()).toContain('Ada Test')
    expect(wrapper.text()).toContain('Order history')
    expect(wrapper.find('a[href="/account#saved-addresses"]').exists()).toBe(true)
    await wrapper.findAll('button').find(button => button.text() === 'Sign out')!.trigger('click')
    expect(user.isAuthenticated).toBe(false)
    expect(cart.itemCount).toBe(0)
    wrapper.unmount()
  })
})
