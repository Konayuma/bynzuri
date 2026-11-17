import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import ProductGallery from '@/components/product/ProductGallery.vue'

describe('ProductGallery', () => {
  it('shows the complete image until the customer chooses to zoom', async () => {
    const wrapper = mount(ProductGallery, { props: { images: [{ id: '1', image: '/product.png', alt_text: 'Conditioner', is_primary: true }] } })
    expect(wrapper.get('img').classes()).toContain('object-contain')
    await wrapper.get('img').trigger('mouseenter')
    expect(wrapper.get('button[aria-label="Zoom in on product image"]').attributes('aria-pressed')).toBe('false')
    await wrapper.get('button[aria-label="Zoom in on product image"]').trigger('click')
    expect(wrapper.get('button[aria-label="Zoom out of product image"]').attributes('aria-pressed')).toBe('true')
    await wrapper.get('button[aria-label="Zoom out of product image"]').trigger('click')
    expect(wrapper.get('button[aria-label="Zoom in on product image"]').attributes('aria-pressed')).toBe('false')
  })
})
