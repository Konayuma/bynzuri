import { describe, expect, it } from 'vitest'
import { formatProductDescription } from '@/utils/productDescription'

describe('product description formatting', () => {
  it('preserves paragraphs, headings and explicit bullet lists', () => {
    expect(formatProductDescription('A gentle serum.\n\nKey Benefits\n\n- Soothes the scalp\n- Supports hydration\n\nHow to use\nApply daily.')).toEqual([
      { type: 'paragraph', text: 'A gentle serum.' },
      { type: 'heading', text: 'Key Benefits' },
      { type: 'list', items: ['Soothes the scalp', 'Supports hydration'] },
      { type: 'heading', text: 'How to use' },
      { type: 'paragraph', text: 'Apply daily.' },
    ])
  })
  it('keeps hyphenated prose and literal markup as text', () => {
    expect(formatProductDescription('A leave-in treatment with <care>.')).toEqual([{ type: 'paragraph', text: 'A leave-in treatment with <care>.' }])
  })
})
