import api from './api'

export interface Payment {
  id: string
  order: string
  method: string
  operator: string
  amount: string
  currency: string
  status: string
  transaction_reference: string
  lenco_reference: string
  phone: string
  fee: string | null
  account_name: string
  created_at: string
}

export const paymentService = {
  async initiatePayment(orderId: string, method: string, phone: string): Promise<Payment> {
    const response = await api.post('/payments/initiate/', {
      order_id: orderId,
      method,
      phone,
    })
    return response.data
  },

  async getPaymentStatus(orderId: string): Promise<Payment> {
    const response = await api.get(`/payments/status/${orderId}/`)
    return response.data
  },

  async pollPaymentStatus(orderId: string, maxAttempts = 8, interval = 3000): Promise<Payment> {
    const deadline = Date.now() + 60000
    for (let i = 0; i < maxAttempts && Date.now() < deadline; i++) {
      const payment = await this.getPaymentStatus(orderId)
      if (payment.status === 'success' || payment.status === 'failed') {
        return payment
      }
      if (Date.now() + interval >= deadline) break
      await new Promise((resolve) => setTimeout(resolve, interval))
    }
    throw new Error('Payment timeout')
  }
}
