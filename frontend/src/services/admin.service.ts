import api from './api'
import type {
  DashboardStats, AdminOrder, PaginatedResponse,
  AdminProvince, AdminTown, AdminDeliveryMethod,
} from '@/types'

export const adminService = {
  async getDashboard(days = 30): Promise<DashboardStats> {
    const response = await api.get('/dashboard/', { params: { days } })
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
  },

  async getProvinces(): Promise<AdminProvince[]> {
    const response = await api.get('/delivery/admin/provinces/')
    return response.data
  },

  async createProvince(data: Partial<AdminProvince>): Promise<AdminProvince> {
    const response = await api.post('/delivery/admin/provinces/', data)
    return response.data
  },

  async updateProvince(id: string, data: Partial<AdminProvince>): Promise<AdminProvince> {
    const response = await api.patch(`/delivery/admin/provinces/${id}/`, data)
    return response.data
  },

  async deleteProvince(id: string): Promise<void> {
    await api.delete(`/delivery/admin/provinces/${id}/`)
  },

  async getTowns(params?: { province?: string }): Promise<AdminTown[]> {
    const response = await api.get('/delivery/admin/towns/', { params })
    return response.data
  },

  async createTown(data: Partial<AdminTown>): Promise<AdminTown> {
    const response = await api.post('/delivery/admin/towns/', data)
    return response.data
  },

  async updateTown(id: string, data: Partial<AdminTown>): Promise<AdminTown> {
    const response = await api.patch(`/delivery/admin/towns/${id}/`, data)
    return response.data
  },

  async deleteTown(id: string): Promise<void> {
    await api.delete(`/delivery/admin/towns/${id}/`)
  },

  async getDeliveryMethods(params?: { is_active?: boolean }): Promise<AdminDeliveryMethod[]> {
    const response = await api.get('/delivery/admin/methods/', { params })
    return response.data
  },

  async createDeliveryMethod(data: Partial<AdminDeliveryMethod>): Promise<AdminDeliveryMethod> {
    const response = await api.post('/delivery/admin/methods/', data)
    return response.data
  },

  async updateDeliveryMethod(id: string, data: Partial<AdminDeliveryMethod>): Promise<AdminDeliveryMethod> {
    const response = await api.patch(`/delivery/admin/methods/${id}/`, data)
    return response.data
  },

  async deleteDeliveryMethod(id: string): Promise<void> {
    await api.delete(`/delivery/admin/methods/${id}/`)
  }
}
