import { describe, it, expect, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import BaseSelect from '@/components/base/BaseSelect.vue'

const options = [
  { value: 'lusaka', label: 'Lusaka' },
  { value: 'copperbelt', label: 'Copperbelt' },
  { value: 'southern', label: 'Southern' },
]

let wrapper: VueWrapper | null = null

afterEach(() => {
  wrapper?.unmount()
  wrapper = null
  document.body.innerHTML = ''
})

describe('BaseSelect', () => {
  it('renders a custom combobox trigger instead of a native select', () => {
    wrapper = mount(BaseSelect, {
      attachTo: document.body,
      props: { label: 'Province', modelValue: '', options, placeholder: 'Choose province', required: true },
    })

    expect(wrapper.find('select').exists()).toBe(false)
    const trigger = wrapper.get('button[role="combobox"]')
    expect(trigger.text()).toContain('Choose province')
    expect(trigger.attributes('aria-expanded')).toBe('false')
    expect(trigger.attributes('aria-required')).toBe('true')
    expect(wrapper.get('label').attributes('for')).toBe(trigger.attributes('id'))
  })

  it('opens the listbox, selects an option, emits update:modelValue, and closes', async () => {
    wrapper = mount(BaseSelect, {
      attachTo: document.body,
      props: {
        label: 'Province',
        modelValue: '',
        options,
        'onUpdate:modelValue': (val: string) => wrapper?.setProps({ modelValue: val }),
      },
    })

    const trigger = wrapper.get('button[role="combobox"]')
    await trigger.trigger('click')
    expect(trigger.attributes('aria-expanded')).toBe('true')

    const renderedOptions = document.body.querySelectorAll<HTMLButtonElement>('[role="option"]')
    expect(renderedOptions.length).toBe(3)

    renderedOptions[1]!.click()
    await wrapper.vm.$nextTick()

    expect(wrapper.props('modelValue')).toBe('copperbelt')
    expect(trigger.text()).toContain('Copperbelt')
    expect(trigger.attributes('aria-expanded')).toBe('false')
    expect(document.body.querySelector('[role="listbox"]')).toBeNull()
  })

  it('supports keyboard navigation (ArrowDown, Enter, Escape)', async () => {
    wrapper = mount(BaseSelect, {
      attachTo: document.body,
      props: {
        modelValue: '',
        options,
        'onUpdate:modelValue': (val: string) => wrapper?.setProps({ modelValue: val }),
      },
    })

    const trigger = wrapper.get('button[role="combobox"]')
    await trigger.trigger('keydown', { key: 'ArrowDown' })
    expect(trigger.attributes('aria-expanded')).toBe('true')

    await trigger.trigger('keydown', { key: 'ArrowDown' })
    await trigger.trigger('keydown', { key: 'Enter' })
    expect(wrapper.props('modelValue')).toBe('copperbelt')
    expect(trigger.attributes('aria-expanded')).toBe('false')

    await trigger.trigger('keydown', { key: 'ArrowUp' })
    expect(trigger.attributes('aria-expanded')).toBe('true')
    await trigger.trigger('keydown', { key: 'Escape' })
    expect(trigger.attributes('aria-expanded')).toBe('false')
  })

  it('closes when clicking outside', async () => {
    wrapper = mount(BaseSelect, {
      attachTo: document.body,
      props: { modelValue: '', options },
    })

    const trigger = wrapper.get('button[role="combobox"]')
    await trigger.trigger('click')
    expect(trigger.attributes('aria-expanded')).toBe('true')

    document.body.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }))
    await wrapper.vm.$nextTick()
    expect(trigger.attributes('aria-expanded')).toBe('false')
  })

  it('does not open when disabled and links error alert via aria-describedby', async () => {
    wrapper = mount(BaseSelect, {
      attachTo: document.body,
      props: { modelValue: '', options, disabled: true, error: 'Select a province.' },
    })

    const trigger = wrapper.get('button[role="combobox"]')
    expect(trigger.attributes('disabled')).toBeDefined()
    expect(trigger.attributes('aria-invalid')).toBe('true')
    expect(trigger.attributes('aria-describedby')).toBe(wrapper.get('[role="alert"]').attributes('id'))

    await trigger.trigger('click')
    expect(trigger.attributes('aria-expanded')).toBe('false')
  })

  it('supports an option with an empty string value (e.g. All Statuses)', () => {
    wrapper = mount(BaseSelect, {
      attachTo: document.body,
      props: {
        modelValue: '',
        options: [
          { value: '', label: 'All Statuses' },
          { value: 'paid', label: 'Paid' },
        ],
      },
    })

    expect(wrapper.get('button[role="combobox"]').text()).toContain('All Statuses')
  })
})
