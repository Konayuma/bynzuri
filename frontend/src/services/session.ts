import { reactive } from 'vue'

export const sessionState = reactive<{ notice: 'expired' | 'unavailable' | null }>({ notice: null })

export function sessionExpired() {
  sessionState.notice = 'expired'
  window.dispatchEvent(new Event('bynzuri:session-expired'))
}

export function sessionUnavailable() {
  if (sessionState.notice !== 'expired') sessionState.notice = 'unavailable'
}

export function sessionRestored() {
  sessionState.notice = null
}
