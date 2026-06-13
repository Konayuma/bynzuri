import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseButton from '@/components/base/BaseButton.vue'

describe('BaseButton', () => {
  it('renders slot content', () => {
    const wrapper = mount(BaseButton, {
      slots: { default: 'Shop Now' }
    })
    expect(wrapper.text()).toBe('Shop Now')
  })

  it('renders primary variant by default', () => {
    const wrapper = mount(BaseButton, {
      slots: { default: 'Click' }
    })
    expect(wrapper.classes()).toContain('bg-primary')
    expect(wrapper.classes()).toContain('text-dark')
  })

  it('renders secondary variant', () => {
    const wrapper = mount(BaseButton, {
      props: { variant: 'secondary' },
      slots: { default: 'Buy' }
    })
    expect(wrapper.classes()).toContain('bg-dark')
    expect(wrapper.classes()).toContain('text-background')
  })

  it('renders outline variant', () => {
    const wrapper = mount(BaseButton, {
      props: { variant: 'outline' },
      slots: { default: 'Browse' }
    })
    expect(wrapper.classes()).toContain('border-2')
    expect(wrapper.classes()).toContain('border-primary')
  })

  it('disables button when disabled prop is true', () => {
    const wrapper = mount(BaseButton, {
      props: { disabled: true },
      slots: { default: 'Buy' }
    })
    expect(wrapper.attributes('disabled')).toBeDefined()
  })

  it('shows loading indicator', () => {
    const wrapper = mount(BaseButton, {
      props: { loading: true },
      slots: { default: 'Saving' }
    })
    const spinner = wrapper.find('svg')
    expect(spinner.exists()).toBe(true)
    expect(wrapper.classes()).toContain('cursor-wait')
  })

  it('emits click event', () => {
    const wrapper = mount(BaseButton, {
      slots: { default: 'Click' }
    })
    wrapper.trigger('click')
    expect(wrapper.emitted('click')).toHaveLength(1)
  })

  it('does not emit click when disabled', () => {
    const wrapper = mount(BaseButton, {
      props: { disabled: true },
      slots: { default: 'Click' }
    })
    wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeUndefined()
  })

  it('applies full width class', () => {
    const wrapper = mount(BaseButton, {
      props: { fullWidth: true },
      slots: { default: 'Full' }
    })
    expect(wrapper.classes()).toContain('w-full')
  })

  it('applies size classes', () => {
    const wrapper = mount(BaseButton, {
      props: { size: 'lg' },
      slots: { default: 'Large' }
    })
    expect(wrapper.classes()).toContain('text-lg')
  })
})
