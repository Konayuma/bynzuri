import { describe, it, expect, vi } from 'vitest'
import { mount, RouterLinkStub } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AdminLayout from '@/layouts/AdminLayout.vue'

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() })
}))

describe('AdminLayout', () => {
  it('provides Back to Site links in both header and sidebar pointing to home', () => {
    setActivePinia(createPinia())
    const wrapper = mount(AdminLayout, {
      global: {
        stubs: { RouterLink: RouterLinkStub },
        mocks: { $route: { path: '/admin' } }
      }
    })

    const headerLink = wrapper.get('header').findComponent(RouterLinkStub)
    expect(headerLink.exists()).toBe(true)
    expect(headerLink.props('to')).toBe('/')
    expect(headerLink.text()).toContain('Back to Site')

    const sidebarBackLinks = wrapper
      .get('aside')
      .findAllComponents(RouterLinkStub)
      .filter((link: { props: (key: string) => unknown; text: () => string }) =>
        link.props('to') === '/' && link.text().includes('Back to Site')
      )
    expect(sidebarBackLinks).toHaveLength(1)
  })
})
