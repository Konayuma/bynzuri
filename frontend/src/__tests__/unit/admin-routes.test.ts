import { describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'
import { adminRoutes } from '@/router/admin'

describe('admin routes', () => {
  const router = createRouter({ history: createMemoryHistory(), routes: adminRoutes })
  it.each(['/admin', '/admin/products', '/admin/orders', '/admin/delivery'])(
    '%s inherits the protected admin area', (path) => {
      const route = router.resolve(path)
      expect(route.name).toBeTruthy()
      expect(route.meta).toMatchObject({ requiresAuth: true, requiresAdmin: true, adminArea: true })
    },
  )
})
