import { describe, expect, it } from 'vitest'
import router from '@/router'

describe('app router guards and fallback', () => {
  it('requires authentication for order confirmation routes', () => {
    const route = router.resolve('/order/confirmation/order-123')
    expect(route.name).toBe('order-confirmation')
    expect(route.meta.requiresAuth).toBe(true)
  })

  it('resolves unknown paths to the 404 not-found route', () => {
    const route = router.resolve('/some/unknown/page')
    expect(route.name).toBe('not-found')
  })
})
