import api, { getAccessToken, publicApi } from './api'

export type SupportTopic = 'order' | 'payment' | 'product' | 'account' | 'returns' | 'general'

export interface SupportInquiryPayload {
  name: string
  email: string
  phone?: string
  topic: SupportTopic
  order_reference?: string
  subject: string
  message: string
  website?: string
}

export interface SupportInquiryResponse {
  id?: string
  reference: string
  detail: string
}

export const supportService = {
  async submitInquiry(payload: SupportInquiryPayload): Promise<SupportInquiryResponse> {
    const client = getAccessToken() ? api : publicApi
    const response = await client.post<SupportInquiryResponse>('/support/inquiries/', payload)
    return response.data
  },
}
