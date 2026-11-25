import { describe, it, expect } from 'vitest'
import { mount, RouterLinkStub } from '@vue/test-utils'
import NotFoundPage from '@/pages/NotFoundPage.vue'

describe('NotFoundPage', () => {
  it('renders the 404 gif, not-found message, and navigation links', () => {
    const wrapper = mount(NotFoundPage, {
      global: {
        stubs: { RouterLink: RouterLinkStub }
      }
    })

    const img = wrapper.get('img')
    expect(img.attributes('src')).toBe('/404.gif')
    expect(wrapper.text()).toContain('Error 404')
    expect(wrapper.text()).toContain('This page could not be found')

    const links = wrapper.findAllComponents(RouterLinkStub).map(l => l.props('to'))
    expect(links).toEqual(['/', '/catalog'])
  })
})
