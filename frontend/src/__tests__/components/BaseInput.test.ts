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

describe('accessible field feedback', () => {
  it('connects its generated label and error to the input', () => {
    const wrapper = mount(BaseInput, { props: { modelValue: '', label: 'Phone', error: 'Enter a number' } })
    const input = wrapper.get('input')
    expect(wrapper.get('label').attributes('for')).toBe(input.attributes('id'))
    expect(input.attributes('aria-invalid')).toBe('true')
    expect(input.attributes('aria-describedby')).toBe(wrapper.get('[role=alert]').attributes('id'))
  })
  it('reveals a password without submitting the form', async () => {
    const wrapper = mount(BaseInput, { props: { modelValue: 'secret', type: 'password', label: 'Password' } })
    await wrapper.get('button').trigger('click')
    expect(wrapper.get('input').attributes('type')).toBe('text')
    expect(wrapper.get('button').attributes('type')).toBe('button')
  })
})
