import api from './api'
import type { Address } from '@/types'

export const addressService = {
  async getAddresses(): Promise<Address[]> {
    const response = await api.get('/auth/addresses/')
    return response.data
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
