/** Accept common Zambian mobile formats without claiming the number is verified. */
export function isZambianPhone(value: string): boolean {
  const compact = value.replace(/[\s()-]/g, '')
  return /^(?:\+?260|0)\d{9}$/.test(compact)
}

export function isZambianMobileMoneyPhone(value: string): boolean {
  return /^(?:\+?260|0)[5679][0-9]{8}$/.test(value.replace(/[\s()-]/g, ''))
}

export function isEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value.trim())
}

export function normalizeZambianPhone(value: string): string {
  const compact = value.replace(/[\s()+-]/g, '')
  return compact.startsWith('0') ? `260${compact.slice(1)}` : compact
}

/** Validate a human name (2–60 chars, letters with optional spaces, hyphens, apostrophes, or periods). */
export function isValidName(value: string): boolean {
  const trimmed = value.trim()
  if (trimmed.length < 2 || trimmed.length > 60) return false
  return /^[\p{L}][\p{L}\s'.-]*[\p{L}.]$/u.test(trimmed)
}

/** Validate a street address or landmark (4–200 chars, must contain letters or numbers). */
export function isValidStreetAddress(value: string): boolean {
  const trimmed = value.trim()
  if (trimmed.length < 4 || trimmed.length > 200) return false
  return /[\p{L}\d]{2,}/u.test(trimmed)
}

const COMMON_PASSWORDS = new Set([
  'password', '12345678', '123456789', '1234567890', 'qwerty123',
  'password1', 'iloveyou', 'admin123', 'letmein1', 'welcome1',
])

export interface PasswordValidationResult {
  valid: boolean
  checks: {
    minLength: boolean
    hasLetter: boolean
    hasNumber: boolean
    notCommon: boolean
  }
  message: string
}

export function validatePassword(value: string): PasswordValidationResult {
  const checks = {
    minLength: value.length >= 8,
    hasLetter: /[A-Za-z]/.test(value),
    hasNumber: /\d/.test(value),
    notCommon: !COMMON_PASSWORDS.has(value.trim().toLowerCase()),
  }

  let message = ''
  if (!checks.minLength) message = 'Use at least 8 characters.'
  else if (!checks.hasLetter || !checks.hasNumber) message = 'Include at least one letter and one number.'
  else if (!checks.notCommon) message = 'Choose a less common password.'

  return {
    valid: checks.minLength && checks.hasLetter && checks.hasNumber && checks.notCommon,
    checks,
    message,
  }
}

export function isValidReviewComment(value: string): boolean {
  const len = value.trim().length
  return len >= 5 && len <= 1000
}
