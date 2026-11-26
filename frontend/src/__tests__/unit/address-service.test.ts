import { describe, expect, it, vi } from 'vitest'
import api from '@/services/api'
import { addressService } from '@/services/address.service'

vi.mock('@/services/api', () => ({ default: { get: vi.fn() } }))

describe('saved addresses', () => {
  it('loads every page without following an external URL', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({ data: { results: [{ id: 'one' }], next: 'https://example.invalid/?page=2' } })
      .mockResolvedValueOnce({ data: { results: [{ id: 'two' }], next: null } })
    const addresses = await addressService.getAddresses()
    expect(addresses.map(item => item.id)).toEqual(['one', 'two'])
    expect(api.get).toHaveBeenNthCalledWith(2, '/auth/addresses/', { params: { page: 2 } })
  })
})
