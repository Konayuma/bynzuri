import api from './api'
import type { Address, PaginatedResponse } from '@/types'

export const addressService = {
  async getAddresses(): Promise<Address[]> {
    const response = await api.get<Address[] | PaginatedResponse<Address>>('/auth/addresses/')
    if (Array.isArray(response.data)) return response.data
    if (!Array.isArray(response.data?.results)) throw new Error('Invalid address response')
    const addresses = [...response.data.results]
    let next = response.data.next
    let page = 2
    while (next) {
      if (page > 100) throw new Error('Too many address pages')
      const more = await api.get<PaginatedResponse<Address>>('/auth/addresses/', { params: { page } })
      if (!Array.isArray(more.data?.results)) throw new Error('Invalid address response')
      addresses.push(...more.data.results)
      next = more.data.next
      page++
    }
    return addresses
  },

  async createAddress(data: {
    province: string
    town: string
    street_address: string
    phone: string
    is_default?: boolean
  }): Promise<Address> {
    const response = await api.post('/auth/addresses/', data)
    return response.data
  },

  async updateAddress(id: string, data: Partial<{
    province: string
    town: string
    street_address: string
    phone: string
    is_default: boolean
  }>): Promise<Address> {
    const response = await api.patch(`/auth/addresses/${id}/`, data)
    return response.data
  },

  async deleteAddress(id: string): Promise<void> {
    await api.delete(`/auth/addresses/${id}/`)
  },
}
