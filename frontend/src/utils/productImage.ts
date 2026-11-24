const signatureImages: Record<string, string> = {
  'growth-elixir': 'growthelixir.webp',
  'nourishing-oil-mix': 'nourishingoilmix.webp',
  'mini-whipped-shea-butter-60g': 'sheabutter.webp',
  'shampoo-bar': 'shampoobar.webp',
  'deep-conditioner': 'deepconditioner.webp',
  'leave-in-conditioner': 'leaveinconditioner.webp',
  'herbal-hair-mist': 'herbalhairmist.webp',
  'exfoliating-toner': 'exfoliatingtoner.webp',
}

export function signatureImage(slug: string): string | undefined {
  const filename = signatureImages[slug]
  return filename ? `/images/products/${filename}` : undefined
}
