import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import DescriptionInline from '@/components/product/DescriptionInline.vue'
import { formatProductDescription } from '@/utils/productDescription'

describe('product description markdown', () => {
  it('renders emphasis, code and safe links without injecting HTML', () => {
    const wrapper = mount(DescriptionInline, { props: { text: '**Serum** with *care*, `daily` and [details](https://example.com). <script>alert(1)</script> [bad](javascript:alert)' } })
    expect(wrapper.get('strong').text()).toBe('Serum')
    expect(wrapper.get('em').text()).toBe('care')
    expect(wrapper.get('code').text()).toBe('daily')
    expect(wrapper.get('a').attributes('href')).toBe('https://example.com')
    expect(wrapper.find('script').exists()).toBe(false)
    expect(wrapper.text()).toContain('[bad](javascript:alert)')
  })

  it('does not mistake bold at the start of a paragraph for a list', () => {
    expect(formatProductDescription('**Your new ritual.** Give your scalp care.\n\n### Benefits\n- **Gentle** care\n\n1. Apply\n2. Massage')).toEqual([
      { type: 'paragraph', text: '**Your new ritual.** Give your scalp care.' },
      { type: 'heading', text: 'Benefits' },
      { type: 'list', items: ['**Gentle** care'] },
      { type: 'list', items: ['Apply', 'Massage'], ordered: true },
    ])
  })
})
