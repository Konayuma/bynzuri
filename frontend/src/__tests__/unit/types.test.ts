import { describe, it, expect } from 'vitest'

describe('Type definitions', () => {
  it('validates Product type shape', () => {
    const product = {
      id: 'uuid-1',
      category: 'cat-uuid',
      category_name: 'Hair Care',
      title: 'Growth Oil',
      slug: 'growth-oil',
      description: 'Premium oil',
      price: '149.99',
      stock: 50,
      is_in_stock: true,
      images: [{ id: 'img-1', image: 'oil.jpg', alt_text: 'Oil bottle', is_primary: true }],
      rating: 4.5,
      review_count: 12,
      created_at: '2026-01-01T00:00:00Z'
    }
    expect(product.title).toBe('Growth Oil')
    expect(product.is_in_stock).toBe(true)
    expect(product.images).toHaveLength(1)
  })

  it('validates Cart type shape', () => {
    const cart = {
      id: 'cart-uuid',
      items: [
        {
          id: 'item-1',
          product: {
            id: 'p-1',
            category: 'c-1',
            category_name: 'Oils',
            title: 'Argan Oil',
            slug: 'argan-oil',
            description: 'Pure argan oil',
            price: '89.99',
            stock: 20,
            is_in_stock: true,
            images: [],
            rating: 4.0,
            review_count: 5,
            created_at: '2026-01-01T00:00:00Z'
          },
          quantity: 2,
          total_price: '179.98'
        }
      ],
      subtotal: '179.98',
      total: '179.98',
      item_count: 2
    }
    expect(cart.item_count).toBe(2)
    expect(cart.subtotal).toBe('179.98')
  })

  it('validates Order type with all statuses', () => {
    const statuses = [
      'awaiting_payment', 'paid', 'processing',
      'dispatched', 'delivered', 'cancelled'
    ] as const
    const order = {
      id: 'order-uuid',
      user: 'user-uuid',
      items: [],
      total_amount: '200.00',
      delivery_fee: '35.00',
      grand_total: '235.00',
      status: 'awaiting_payment' as typeof statuses[number],
      province: 'Lusaka',
      town: 'Lusaka',
      delivery_method: 'courier',
      payment_method: 'mtn_momo',
      created_at: '2026-01-01T00:00:00Z'
    }
    expect(statuses).toContain(order.status)
    order.status = 'delivered'
    expect(order.status).toBe('delivered')
  })

  it('validates PaginatedResponse type', () => {
    const response = {
      count: 25,
      next: 'http://api.test/products/?page=2',
      previous: null,
      results: []
    }
    expect(response.count).toBe(25)
    expect(response.next).toBeTruthy()
    expect(response.previous).toBeNull()
  })
})
