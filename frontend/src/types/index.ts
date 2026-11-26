export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  phone: string
  role: 'customer' | 'admin'
  is_staff?: boolean
  email_verified?: boolean
}

export interface AuthTokens {
  access: string
}

export interface Category {
  id: string
  name: string
  slug: string
  image: string
  product_count: number
}

export interface ProductImage {
  id: string
  image: string
  alt_text: string
  is_primary: boolean
}

export interface Product {
  id: string
  category: string
  category_name: string
  category_slug?: string
  title: string
  slug: string
  description: string
  price: string
  sale_price?: string
  discount_percent?: string
  effective_discount_percent?: string
  stock: number
  is_in_stock: boolean
  is_active?: boolean
  is_featured?: boolean
  images: ProductImage[]
  rating: number
  review_count: number
  created_at: string
}

export interface CartItem {
  id: string
  product: Product
  quantity: number
  total_price: string
}

export interface Cart {
  id: string
  items: CartItem[]
  subtotal: string
  total: string
  item_count: number
}

export interface Province {
  id: string
  name: string
}

export interface Town {
  id: string
  province: string
  name: string
}

export interface DeliveryMethod {
  id: string
  name: string
  description: string
  price: string
  estimated_days: string
}

export interface Order {
  id: string
  user: string
  items: OrderItem[]
  item_count?: number
  total_amount: string
  delivery_fee: string
  grand_total: string
  status: OrderStatus
  province: string
  town: string
  delivery_method: string
  payment_method: string
  created_at: string
}

export interface OrderItem {
  id: string
  product: string
  product_title: string
  quantity: number
  price_at_purchase: string
}

export type OrderStatus =
  | 'awaiting_payment'
  | 'paid'
  | 'processing'
  | 'dispatched'
  | 'delivered'
  | 'cancelled'

export interface Review {
  id: string
  product: string
  user: string
  user_name: string
  staff_reply: string
  is_approved: boolean
  rating: number
  comment: string
  created_at: string
}

export interface Address {
  id: string
  user?: string
  province: string
  province_name: string
  town: string
  town_name: string
  street_address: string
  phone: string
  is_default: boolean
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface WishlistItem {
  id: string
  product: Product
  added_at: string
}

export interface ApiError {
  detail: string
  [key: string]: string | string[] | undefined
}

export interface DashboardStats {
  revenue: string | number
  orders: number
  products: number
  customers: number
  orders_by_status: { status: string; count: number }[]
  recent_orders: Order[]
  low_stock: { id: string; title: string; stock: number }[]
  period_days: number
  period_revenue: string | number
  period_orders: number
  sales_history: { date: string; revenue: string | number; orders: number }[]
  top_products: { product_title: string; units: number; revenue: string | number }[]
}

export interface AdminProvince {
  id: string
  name: string
  slug: string
  sort_order: number
}

export interface AdminTown {
  id: string
  province: string
  province_name: string
  name: string
  slug: string
}

export interface AdminDeliveryMethod {
  id: string
  name: string
  description: string
  price: string
  estimated_days: string
  is_active: boolean
  sort_order: number
}

export interface AdminOrder extends Order {
  user_email: string
  user_name: string
  street_address: string
  phone: string
  notes: string
  updated_at: string
}

export interface ProductCreateData {
  category: string
  title: string
  slug: string
  description: string
  price: string
  discount_percent: string
  stock: number
  is_active: boolean
  is_featured: boolean
}
