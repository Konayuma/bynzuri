const key = 'bynzuri_verification_email'
let currentEmail = ''

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
