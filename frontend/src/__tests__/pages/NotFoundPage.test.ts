import { describe, it, expect, vi, afterEach } from 'vitest'
import { mount, RouterLinkStub } from '@vue/test-utils'
import NotFoundPage from '@/pages/NotFoundPage.vue'

describe('NotFoundPage', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    Object.defineProperty(navigator, 'connection', { value: undefined, configurable: true })
  })

  it('renders the lightweight poster, looping video sources, message, and navigation links', async () => {
    const wrapper = mount(NotFoundPage, {
      global: {
        stubs: { RouterLink: RouterLinkStub }
      }
    })
    await wrapper.vm.$nextTick()

    expect(wrapper.get('img').attributes('src')).toBe('/404-poster.webp')
    const sources = wrapper.findAll('video source').map(s => s.attributes('src'))
    expect(sources).toEqual(['/404.mp4'])
    expect(wrapper.text()).toContain('Error 404')
    expect(wrapper.text()).toContain('This page could not be found')

    const links = wrapper.findAllComponents(RouterLinkStub).map(l => l.props('to'))
    expect(links).toEqual(['/', '/catalog'])
  })

  it('skips loading video on Save-Data or slow 2G connections and shows the static poster', async () => {
    Object.defineProperty(navigator, 'connection', {
      value: { saveData: true, effectiveType: '2g' },
      configurable: true
    })

    const wrapper = mount(NotFoundPage, {
      global: {
        stubs: { RouterLink: RouterLinkStub }
      }
    })
    await wrapper.vm.$nextTick()

    expect(wrapper.get('img').attributes('src')).toBe('/404-poster.webp')
    expect(wrapper.find('video').exists()).toBe(false)
  })
})
