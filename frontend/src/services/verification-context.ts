const key = 'bynzuri_verification_email'
let currentEmail = ''
let pendingSignup: { email: string; password: string; expiresAt: number } | null = null
let pendingTimer: ReturnType<typeof setTimeout> | undefined

export function rememberVerificationEmail(email: string) {
  currentEmail = email.trim()
  try {
    if (currentEmail) sessionStorage.setItem(key, currentEmail)
    else sessionStorage.removeItem(key)
  } catch { /* Keep the address in memory when browser storage is unavailable. */ }
}

export function getVerificationEmail(): string {
  try { return currentEmail || sessionStorage.getItem(key) || '' }
  catch { return currentEmail }
}

// Passwords stay only in memory and are consumed once after verification.
export function rememberSignupCredentials(email: string, password: string) {
  clearSignupCredentials()
  pendingSignup = { email: email.trim().toLowerCase(), password, expiresAt: Date.now() + 30 * 60 * 1000 }
  pendingTimer = setTimeout(clearSignupCredentials, 30 * 60 * 1000)
}

export function takeSignupCredentials(email: string): { email: string; password: string } | null {
  const pending = pendingSignup
  clearSignupCredentials()
  if (!pending || pending.expiresAt <= Date.now() || pending.email !== email.trim().toLowerCase()) return null
  return { email: pending.email, password: pending.password }
}

export function clearSignupCredentials() {
  pendingSignup = null
  if (pendingTimer) clearTimeout(pendingTimer)
  pendingTimer = undefined
}
