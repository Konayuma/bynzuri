import { nextTick, onBeforeUnmount, watch, type Ref } from 'vue'

const selector = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'

export function useDialogFocus(open: () => boolean, panel: Ref<HTMLElement | null>, close: () => void) {
  let previous: HTMLElement | null = null
  let previousOverflow = ''
  let active = false
  function onKeydown(event: KeyboardEvent) {
    if (!active) return
    if (event.key === 'Escape') { event.preventDefault(); close(); return }
    if (event.key !== 'Tab' || !panel.value) return
    const focusable = [...panel.value.querySelectorAll<HTMLElement>(selector)].filter(el => !el.hidden && el.getAttribute('aria-hidden') !== 'true')
    if (!focusable.length) { event.preventDefault(); panel.value.focus(); return }
    const index = focusable.indexOf(document.activeElement as HTMLElement)
    if (event.shiftKey && index <= 0) { event.preventDefault(); focusable[focusable.length - 1]!.focus() }
    else if (!event.shiftKey && (index < 0 || index === focusable.length - 1)) { event.preventDefault(); focusable[0]!.focus() }
  }
  function deactivate() {
    if (!active) return
    active = false
    document.removeEventListener('keydown', onKeydown)
    document.body.style.overflow = previousOverflow
    if (previous?.isConnected) previous.focus()
    previous = null
  }
  watch(open, async isOpen => {
    if (!isOpen) { deactivate(); return }
    previous = document.activeElement instanceof HTMLElement ? document.activeElement : null
    previousOverflow = document.body.style.overflow
    active = true
    document.body.style.overflow = 'hidden'
    document.addEventListener('keydown', onKeydown)
    await nextTick()
    if (active) (panel.value?.querySelector<HTMLElement>(selector) || panel.value)?.focus()
  }, { immediate: true })
  onBeforeUnmount(deactivate)
}
