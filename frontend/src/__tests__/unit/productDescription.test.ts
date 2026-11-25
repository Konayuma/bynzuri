import { describe, it, expect } from 'vitest'
import { formatProductDescription } from '@/utils/productDescription'

describe('formatProductDescription', () => {
  it('parses paragraphs, plain-text and markdown headings, and bullet lists with or without spaces', () => {
    const input = `Your new targeted scalp care ritual.

## Key Benefits
-Reduce visible dandruff and scalp flakes.
- Relieve the feeling of an itchy, uncomfortable scalp.
• Maintain scalp hydration and support the skin barrier.

Who is it best for?
Root Revival is ideal for anyone experiencing:
- Dandruff and recurring scalp flakes.
- Scalp buildup from oils.

How to use
Apply directly to the scalp, concentrating on areas of concern.`

    expect(formatProductDescription(input)).toEqual([
      { type: 'paragraph', text: 'Your new targeted scalp care ritual.' },
      { type: 'heading', text: 'Key Benefits' },
      {
        type: 'list',
        items: [
          'Reduce visible dandruff and scalp flakes.',
          'Relieve the feeling of an itchy, uncomfortable scalp.',
          'Maintain scalp hydration and support the skin barrier.',
        ],
      },
      { type: 'heading', text: 'Who is it best for?' },
      { type: 'paragraph', text: 'Root Revival is ideal for anyone experiencing:' },
      {
        type: 'list',
        items: [
          'Dandruff and recurring scalp flakes.',
          'Scalp buildup from oils.',
        ],
      },
      { type: 'heading', text: 'How to use' },
      { type: 'paragraph', text: 'Apply directly to the scalp, concentrating on areas of concern.' },
    ])
  })
})
