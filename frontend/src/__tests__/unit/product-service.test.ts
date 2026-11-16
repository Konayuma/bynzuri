import { describe, expect, it, vi } from 'vitest'
import api, { publicApi } from '@/services/api'
import { productService } from '@/services/product.service'

describe('guest product browsing', () => {
  it('uses the unauthenticated client and translates category filters', async () => {
    localStorage.setItem('access_token', 'expired-token')
    const publicGet = vi.spyOn(publicApi, 'get').mockResolvedValueOnce({ data: { results: [], count: 0 } })
    const privateGet = vi.spyOn(api, 'get')
    await productService.getProducts({ search: 'growth', category: 'hair-care' })
    expect(publicGet).toHaveBeenCalledWith('/products/', { params: { search: 'growth', category: undefined, category__slug: 'hair-care' } })
    expect(privateGet).not.toHaveBeenCalled()
    publicGet.mockRestore()
    privateGet.mockRestore()
    localStorage.clear()
  })
})
