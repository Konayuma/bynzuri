const signatureImages: Record<string, string> = {
  'growth-elixir': 'growthelixir.png',
  'nourishing-oil-mix': 'nourishingoilmix.png',
  'mini-whipped-shea-butter-60g': 'sheabutter.png',
  'shampoo-bar': 'shampoobar.png',
  'deep-conditioner': 'deepconditioner.png',
  'leave-in-conditioner': 'leaveinconditioner.png',
  'herbal-hair-mist': 'herbalhairmist.png',
  'exfoliating-toner': 'exfoliatingtoner.png',
}

export function signatureImage(slug: string): string | undefined {
  const filename = signatureImages[slug]
  return filename ? `/images/products/${filename}` : undefined
}
