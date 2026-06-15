import api from './api'
import type { DashboardStats, AdminOrder, PaginatedResponse } from '@/types'

export const adminService = {
  async getDashboard(): Promise<DashboardStats> {
    const response = await api.get('/dashboard/')
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
