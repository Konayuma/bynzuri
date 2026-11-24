import { describe, expect, it } from 'vitest'
import { isEmail, isZambianPhone, isZambianMobileMoneyPhone, normalizeZambianPhone } from '@/utils/formValidation'

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
  it('aligns mobile-money validation with the payment API', () => {
    for (const phone of ['0571234567', '0771234567', '0971234567', '+260 571 234 567']) expect(isZambianMobileMoneyPhone(phone)).toBe(true)
    for (const phone of ['0111234567', '097123456', '+2600971234567', '09712345678']) expect(isZambianMobileMoneyPhone(phone)).toBe(false)
  })
})
