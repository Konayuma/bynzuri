import { describe, it, expect, vi } from 'vitest'
import { flushPromises, mount, RouterLinkStub } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AdminLayout from '@/layouts/AdminLayout.vue'
import { authService } from '@/services/auth.service'
import { useUserStore } from '@/stores/user'
import { useUIStore } from '@/stores/ui'

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

  it('confirms sign-out from the admin area', async () => {
    setActivePinia(createPinia())
    const logout = vi.spyOn(authService, 'logout').mockResolvedValue()
    const user = useUserStore()
    user.user = { id: '1', email: 'admin@example.com', first_name: '', last_name: '', phone: '', role: 'admin', is_staff: true }
    const wrapper = mount(AdminLayout, { global: { stubs: { RouterLink: RouterLinkStub }, mocks: { $route: { path: '/admin' } } } })
    await wrapper.findAll('button').find(button => button.text() === 'Sign Out')!.trigger('click')
    await flushPromises()
    expect(user.user).toBeNull()
    expect(useUIStore().toast?.message).toContain('signed out')
    logout.mockRestore()
  })
})
