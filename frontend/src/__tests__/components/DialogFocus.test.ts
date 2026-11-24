import { afterEach, describe, expect, it } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import BaseModal from '@/components/base/BaseModal.vue'
import BaseDrawer from '@/components/base/BaseDrawer.vue'

describe.each([['modal', BaseModal], ['drawer', BaseDrawer]])('%s focus management', (_name, Component) => {
  afterEach(() => { document.body.innerHTML = ''; document.body.style.overflow = '' })
  it('moves focus into the dialog, confines Tab, closes on Escape and restores focus', async () => {
    const trigger = document.createElement('button')
    document.body.appendChild(trigger)
    trigger.focus()
    const wrapper = mount(Component, { attachTo: document.body, props: { open: false, title: 'Example' }, slots: { default: '<button>Confirm</button>' } })
    await wrapper.setProps({ open: true })
    await flushPromises()
    expect(document.activeElement?.getAttribute('aria-label')).toBe('Close')
    const buttons = document.querySelectorAll<HTMLElement>('[role="dialog"] button')
    buttons[buttons.length - 1]!.focus()
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', bubbles: true, cancelable: true }))
    expect(document.activeElement).toBe(buttons[0])
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true, cancelable: true }))
    expect(wrapper.emitted('close')).toHaveLength(1)
    await wrapper.setProps({ open: false })
    expect(document.activeElement).toBe(trigger)
    expect(document.body.style.overflow).toBe('')
    wrapper.unmount()
  })
})
