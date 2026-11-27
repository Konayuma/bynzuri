export type AuthMethod = 'google' | 'email'

const STORAGE_KEY = 'bynzuri_last_auth_method'

export function getLastAuthMethod(): AuthMethod | null {
  try {
    const value = localStorage.getItem(STORAGE_KEY)
    return value === 'google' || value === 'email' ? value : null
  } catch {
    return null
  }
}

export function setLastAuthMethod(method: AuthMethod): void {
  try {
    localStorage.setItem(STORAGE_KEY, method)
  } catch {
    // Ignore storage errors in restricted browsing modes.
  }
}
