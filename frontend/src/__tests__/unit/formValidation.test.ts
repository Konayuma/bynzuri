import { describe, expect, it } from 'vitest'
import {
  isEmail,
  isZambianPhone,
  isZambianMobileMoneyPhone,
  normalizeZambianPhone,
  isValidName,
  isValidStreetAddress,
  validatePassword,
  isValidReviewComment,
} from '@/utils/formValidation'

describe('form validation', () => {
  it('checks complete email addresses', () => {
    expect(isEmail('shop@example.com')).toBe(true)
    expect(isEmail('shop@example')).toBe(false)
    expect(isEmail('shop@example.c')).toBe(false)
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
  it('validates names and street addresses', () => {
    expect(isValidName('Monica')).toBe(true)
    expect(isValidName("O'Brien-K")).toBe(true)
    expect(isValidName('A')).toBe(false)
    expect(isValidName('12345')).toBe(false)

    expect(isValidStreetAddress('Plot 42, Kabulonga Rd')).toBe(true)
    expect(isValidStreetAddress('...')).toBe(false)
    expect(isValidStreetAddress('ab')).toBe(false)
  })
  it('validates password strength and rejects weak/common passwords', () => {
    expect(validatePassword('password123').valid).toBe(true)
    expect(validatePassword('short1').valid).toBe(false)
    expect(validatePassword('onlyletters').valid).toBe(false)
    expect(validatePassword('12345678').valid).toBe(false)
    expect(validatePassword('qwerty123').valid).toBe(false)
  })
  it('validates review comment length', () => {
    expect(isValidReviewComment('Great hair oil!')).toBe(true)
    expect(isValidReviewComment('Nice')).toBe(false)
    expect(isValidReviewComment('a'.repeat(1001))).toBe(false)
  })
})
