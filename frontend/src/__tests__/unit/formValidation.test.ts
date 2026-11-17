import { describe, expect, it } from 'vitest'
import { isEmail, isZambianPhone, normalizeZambianPhone } from '@/utils/formValidation'

describe('form validation', () => {
  it('checks complete email addresses', () => {
    expect(isEmail('shop@example.com')).toBe(true)
    expect(isEmail('shop@example')).toBe(false)
  })
  it('accepts and normalizes Zambian numbers for payment', () => {
    for (const phone of ['0971234567', '260971234567', '+260 971 234 567']) {
      expect(isZambianPhone(phone)).toBe(true)
      expect(normalizeZambianPhone(phone)).toBe('260971234567')
    }
    expect(isZambianPhone('260')).toBe(false)
    expect(isZambianPhone('1234567890')).toBe(false)
  })
})
