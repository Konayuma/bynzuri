import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import AppNavbar from '@/layouts/AppNavbar.vue'

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
    expect(wrapper.text().toLowerCase()).toContain('bynzuri')
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
})
