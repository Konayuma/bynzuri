import { describe, it, expect, beforeEach, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import HelpPage from '@/pages/HelpPage.vue'
import { supportService } from '@/services/support.service'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div />' } },
    { path: '/help', component: HelpPage },
    { path: '/catalog', component: { template: '<div />' } },
    { path: '/account/orders', component: { template: '<div />' } },
    { path: '/auth/forgot-password', component: { template: '<div />' } },
  ],
})

function mountHelpPage() {
  return mount(HelpPage, {
    global: {
      plugins: [router],
    },
  })
}

describe('HelpPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  it('renders help content, inquiry form, and the configured support email', () => {
    const wrapper = mountHelpPage()
    expect(wrapper.text()).toContain('How can we help?')
    expect(wrapper.text()).toContain('Send an Inquiry')
    expect(wrapper.text()).toContain('hairskincare@bynzuri.com')
    expect(wrapper.html()).not.toContain('hello@bynzuri.zm')
  })

  it('shows validation errors when submitting an empty inquiry form', async () => {
    const submitSpy = vi.spyOn(supportService, 'submitInquiry')
    const wrapper = mountHelpPage()

    await wrapper.find('form').trigger('submit')
    expect(submitSpy).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('Enter your name')
    expect(wrapper.text()).toContain('Enter your email address.')
    expect(wrapper.text()).toContain('Enter a short subject')
    expect(wrapper.text()).toContain('Please enter at least 10 characters')
  })

  it('submits a valid inquiry and displays the reference confirmation', async () => {
    const submitSpy = vi.spyOn(supportService, 'submitInquiry').mockResolvedValue({
      id: '11111111-2222-3333-4444-555555555555',
      reference: 'SUP-11111111',
      detail: 'Your inquiry has been received. Our team will reply by email.',
    })
    const wrapper = mountHelpPage()

    await wrapper.get('#support-name').setValue('Chanda Banda')
    await wrapper.get('#support-email').setValue('chanda@example.com')
    await wrapper.get('#support-subject').setValue('Order question')
    await wrapper.get('#support-message').setValue('Could you please share an update on my delivery?')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(submitSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        name: 'Chanda Banda',
        email: 'chanda@example.com',
        topic: 'general',
        subject: 'Order question',
        message: 'Could you please share an update on my delivery?',
      })
    )
    expect(wrapper.text()).toContain('Inquiry Sent')
    expect(wrapper.text()).toContain('SUP-11111111')
    expect(wrapper.text()).toContain('chanda@example.com')
  })

  it('pre-fills name and email for signed-in users', async () => {
    const userStore = useUserStore()
    userStore.user = {
      id: 'u1',
      first_name: 'Ada',
      last_name: 'Lovelace',
      email: 'ada@example.com',
      phone: '+260977000000',
      role: 'customer',
      is_staff: false,
      email_verified: true,
    }
    const wrapper = mountHelpPage()
    await flushPromises()

    expect((wrapper.get('#support-name').element as HTMLInputElement).value).toBe('Ada Lovelace')
    expect((wrapper.get('#support-email').element as HTMLInputElement).value).toBe('ada@example.com')
    expect((wrapper.get('#support-phone').element as HTMLInputElement).value).toBe('+260977000000')
  })

  it('displays a friendly error message when rate limited', async () => {
    vi.spyOn(supportService, 'submitInquiry').mockRejectedValue({
      response: { status: 429 },
    })
    const wrapper = mountHelpPage()

    await wrapper.get('#support-name').setValue('Chanda Banda')
    await wrapper.get('#support-email').setValue('chanda@example.com')
    await wrapper.get('#support-subject').setValue('Order question')
    await wrapper.get('#support-message').setValue('Could you please share an update on my delivery?')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('several inquiries recently')
  })
})
