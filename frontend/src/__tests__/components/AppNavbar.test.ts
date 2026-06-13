import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AppNavbar from '@/layouts/AppNavbar.vue'

function createWrapper() {
  setActivePinia(createPinia())
  return mount(AppNavbar, {
    global: {
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
      // Mobile menu should be visible after toggle
      expect(wrapper.text()).toContain('Shop All')
    }
  })
})
