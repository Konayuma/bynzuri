import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseInput from '@/components/base/BaseInput.vue'

describe('BaseInput', () => {
  it('renders label', () => {
    const wrapper = mount(BaseInput, {
      props: { label: 'Email', modelValue: '' }
    })
    expect(wrapper.find('label').text()).toBe('Email')
  })

  it('renders required asterisk', () => {
    const wrapper = mount(BaseInput, {
      props: { label: 'Name', modelValue: '', required: true }
    })
    expect(wrapper.find('label').html()).toContain('*')
  })

  it('renders placeholder', () => {
    const wrapper = mount(BaseInput, {
      props: { modelValue: '', placeholder: 'Enter your name' }
    })
    expect(wrapper.find('input').attributes('placeholder')).toBe('Enter your name')
  })

  it('updates model value on input', async () => {
    const wrapper = mount(BaseInput, {
      props: { modelValue: '', 'onUpdate:modelValue': (e: string) => wrapper.setProps({ modelValue: e }) }
    })
    const input = wrapper.find('input')
    await input.setValue('test@email.com')
    expect(wrapper.props('modelValue')).toBe('test@email.com')
  })

  it('shows error message', () => {
    const wrapper = mount(BaseInput, {
      props: { modelValue: '', error: 'This field is required' }
    })
    expect(wrapper.find('p').text()).toBe('This field is required')
  })

  it('disables input', () => {
    const wrapper = mount(BaseInput, {
      props: { modelValue: '', disabled: true }
    })
    expect(wrapper.find('input').attributes('disabled')).toBeDefined()
  })

  it('sets input type', () => {
    const wrapper = mount(BaseInput, {
      props: { modelValue: '', type: 'email' }
    })
    expect(wrapper.find('input').attributes('type')).toBe('email')
  })
})
