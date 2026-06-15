import api from './api'
import type { Order, DeliveryMethod, Province, Town, AdminOrder, PaginatedResponse } from '@/types'

export const orderService = {
  async createOrder(data: {
    province: string
    town: string
    delivery_method: string
    payment_method: string
    street_address: string
    phone: string
    notes?: string
  }): Promise<Order> {
    const response = await api.post('/orders/', data)
    return response.data
  },

  async getOrder(id: string): Promise<Order> {
    const response = await api.get(`/orders/${id}/`)
    return response.data
  },

  async getOrders(): Promise<Order[]> {
    const response = await api.get('/orders/')
    return response.data
  },

  async getProvinces(): Promise<Province[]> {
    const response = await api.get('/delivery/provinces/')
    return response.data
  },

  async getTowns(provinceId: string): Promise<Town[]> {
    const response = await api.get(`/delivery/towns/?province=${provinceId}`)
    return response.data
  },

  async getDeliveryMethods(): Promise<DeliveryMethod[]> {
    const response = await api.get('/delivery/methods/')
    return response.data
  },

  async getAllOrders(params?: {
    page?: number
    status?: string
  }): Promise<PaginatedResponse<AdminOrder>> {
    const response = await api.get('/orders/admin/', { params })
    return response.data
  },

  async updateOrderStatus(id: string, status: string): Promise<AdminOrder> {
    const response = await api.patch(`/orders/admin/${id}/status/`, { status })
    return response.data
  }
}
