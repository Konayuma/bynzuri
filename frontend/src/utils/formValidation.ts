/** Accept common Zambian mobile formats without claiming the number is verified. */
export function isZambianPhone(value: string): boolean {
  const compact = value.replace(/[\s()-]/g, '')
  return /^(?:\+?260|0)\d{9}$/.test(compact)
}

export function isZambianMobileMoneyPhone(value: string): boolean {
  return /^(?:\+?260|0)[5679][0-9]{8}$/.test(value.replace(/[\s()-]/g, ''))
}

export function isEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim())
}

export function normalizeZambianPhone(value: string): string {
  const compact = value.replace(/[\s()+-]/g, '')
  return compact.startsWith('0') ? `260${compact.slice(1)}` : compact
}
