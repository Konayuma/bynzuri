<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useProductStore } from '@/stores/product'
import ProductCard from '@/components/product/ProductCard.vue'
import ProductGridSkeleton from '@/components/product/ProductGridSkeleton.vue'
import ProductStoryHero from '@/components/home/ProductStoryHero.vue'
const productStore = useProductStore()
const productsError = ref(false)
async function loadProducts() {
  productsError.value = false
  try { await productStore.fetchProducts() } catch { productsError.value = true }
}
onMounted(loadProducts)
</script>

<template>
<div class="stitch-landing">


<!-- 1. HERO SECTION WITH MINIMALIST HEADER & WARM AMBIENT GLOW -->
<!-- ============================================== -->
<ProductStoryHero />
<!-- ============================================== -->
<!-- 2. "OUR BEST SELLERS" PRODUCT ROW -->
<!-- ============================================== -->
<section id="sellers" class="w-full bg-[#fbf9f8] py-20 sm:py-24">
  <div class="max-w-7xl mx-auto px-6 sm:px-12">
    <div class="flex flex-wrap items-end justify-between gap-4 mb-10">
      <div><span class="text-[11px] font-felix tracking-[0.2em] uppercase text-stone-500 block mb-2">Curated Formulations</span><h2 class="text-3xl sm:text-4xl font-felix text-stone-900">Our <span class="font-sinfonietta text-4xl sm:text-5xl">Signature</span> Collection</h2></div>
      <router-link to="/catalog" class="text-xs font-felix uppercase tracking-wider underline underline-offset-4">Shop all products</router-link>
    </div>
    <ProductGridSkeleton v-if="productStore.loading" message="Loading the collection…" />
    <div v-else-if="productsError" role="alert" class="text-sm text-muted"><p>Products are temporarily unavailable.</p><button type="button" class="mt-3 min-h-11 underline text-dark" @click="loadProducts">Try again</button></div>
    <p v-else-if="!productStore.products.length" class="text-sm text-muted">There are no products available yet.</p>
    <div v-else class="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6"><ProductCard v-for="product in productStore.products.slice(0, 4)" :key="product.id" :product="product" /></div>
  </div>
</section>
<section class="w-full bg-white py-20" aria-labelledby="shop-products-title">
  <div class="max-w-7xl mx-auto px-6 sm:px-12">
    <div class="flex flex-wrap items-end justify-between gap-4 mb-10"><div><span class="text-[11px] font-felix tracking-[0.2em] uppercase text-stone-500 block mb-2">The Nzuri Shop</span><h2 id="shop-products-title" class="text-3xl sm:text-4xl font-felix text-stone-900">Shop Our Products</h2></div><router-link to="/catalog" class="text-xs font-felix uppercase tracking-wider underline underline-offset-4">View all</router-link></div>
    <ProductGridSkeleton v-if="productStore.loading" message="Loading more products…" />
    <p v-else-if="productsError" class="text-sm text-stone-500">Products are temporarily unavailable. Use the retry button above to try again.</p>
    <p v-else-if="productStore.products.length <= 4" class="text-sm text-stone-500">Explore our full collection in the catalog.</p>
    <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6"><ProductCard v-for="product in productStore.products.slice(4, 12)" :key="product.id" :product="product" /></div>
  </div>
</section>
<!-- ============================================== -->
<!-- 3. MISSION / STATEMENT CALLOUT SECTION (WARM SAND / CLAY) -->
<!-- ============================================== -->
<section class="relative w-full bg-[#dcbec3] py-24 sm:py-32 overflow-hidden text-center" id="about"><div class="pointer-events-none absolute inset-x-0 bottom-4 text-center z-0 select-none opacity-20 overflow-hidden"><span class="text-[18vw] font-felix font-bold uppercase tracking-[0.2em] text-white block">NZURI</span></div><div class="relative z-10 max-w-4xl mx-auto px-6 sm:px-12 flex flex-col items-center"><div class="inline-block px-4 py-1.5 rounded-full bg-white/70 border border-white text-[11px] font-felix font-semibold uppercase tracking-[0.25em] text-stone-800 mb-6">Our Brand Story • Founded 2018</div><h2 class="text-2xl sm:text-4xl lg:text-5xl font-felix font-normal text-stone-900 leading-tight max-w-3xl mb-6">HAIR AND SKINCARE BY NZURI IS DEDICATED TO <span class="font-sinfonietta text-4xl sm:text-5xl lg:text-6xl text-stone-950 block mt-1">Safe Organic Formulations</span></h2><p class="text-sm sm:text-base text-stone-800 max-w-2xl font-light leading-relaxed mb-10">We create beauty essentials crafted from raw, natural ingredients with the aim of ensuring your hair and skin are completely free from toxic chemicals such as sulphates, parabens, and mineral oils.</p><div class="grid grid-cols-2 sm:grid-cols-4 gap-4 w-full max-w-2xl mb-12"><div class="p-3 bg-white/80 rounded-xl shadow-sm border border-white/60"><span class="text-xs font-felix font-bold text-stone-900 block">SULPHATE-FREE</span><span class="text-[10px] text-stone-600">Gentle cleansing</span></div><div class="p-3 bg-white/80 rounded-xl shadow-sm border border-white/60"><span class="text-xs font-felix font-bold text-stone-900 block">PARABEN-FREE</span><span class="text-[10px] text-stone-600">Zero toxins</span></div><div class="p-3 bg-white/80 rounded-xl shadow-sm border border-white/60"><span class="text-xs font-felix font-bold text-stone-900 block">NO MINERAL OIL</span><span class="text-[10px] text-stone-600">Pure botanicals</span></div><div class="p-3 bg-white/80 rounded-xl shadow-sm border border-white/60"><span class="text-xs font-felix font-bold text-stone-900 block">100% ORGANIC</span><span class="text-[10px] text-stone-600">Sustainably crafted</span></div></div><div class="relative transform rotate-1 hover:rotate-0 transition-transform duration-500 shadow-2xl rounded-2xl overflow-hidden max-w-sm sm:max-w-md border-4 border-white"><img loading="lazy" decoding="async" alt="Hair and Skincare by Nzuri product line" class="w-full h-80 sm:h-96 object-cover" src="/images/products/deepconditioner.webp"/></div></div></section>
<!-- ============================================== -->
<!-- 4. "OUR KEY ADVANTAGES" TRUST ROW -->
<!-- ============================================== -->
<section class="w-full bg-[#fcf9f9] py-16 sm:py-24"><div class="max-w-7xl mx-auto px-6 sm:px-12"><div class="rounded-3xl overflow-hidden grid grid-cols-1 lg:grid-cols-12 shadow-xl border border-stone-200/80"><div class="lg:col-span-6 relative min-h-[460px] lg:min-h-full"><img loading="lazy" decoding="async" alt="By Nzuri product" class="absolute inset-0 w-full h-full object-cover" src="/images/products/shampoobar.webp"/></div><div class="lg:col-span-6 bg-[#dcbec3] p-8 sm:p-14 text-stone-900 flex flex-col justify-center"><div class="mb-8"><span class="text-[11px] font-felix tracking-[0.2em] uppercase font-bold text-stone-800 block mb-2">Pure Hair &amp; Skin Wellness</span><h2 class="text-3xl sm:text-4xl font-felix font-normal text-stone-900 leading-tight">It's Time to <span class="font-sinfonietta text-4xl sm:text-5xl text-stone-950 block mt-1">Upgrade Your Routine</span></h2><p class="text-xs text-stone-700 font-light mt-3 leading-relaxed">Handcrafted with certified organic botanical oils, soothing hydrators, and nutrient-dense raw butters to give lasting radiance.</p></div><div class="space-y-3.5"><div class="bg-white rounded-2xl p-6 text-stone-900 shadow-md border border-white"><h3 class="text-sm font-felix font-bold mb-2 uppercase tracking-wide">Organic &amp; Toxic-Free Ingredients</h3><p class="text-xs text-stone-600 leading-relaxed font-light mb-4">Formulated free from parabens, harsh sulphates, and synthetic fillers for healthy scalp stimulation and hydrated, supple skin.</p><a class="text-xs font-felix font-bold text-stone-900 underline hover:text-stone-700 tracking-wider uppercase" href="#sellers">Explore All Formulations →</a></div><div class="bg-white/50 backdrop-blur rounded-2xl px-6 py-4 flex items-center justify-between text-xs font-felix font-semibold text-stone-900 hover:bg-white/70 transition-all cursor-pointer border border-white/60"><span class="tracking-wide uppercase">Nourishing Scalp &amp; Follicle Care</span><span class="material-symbols-outlined text-[16px]">arrow_forward</span></div><div class="bg-white/50 backdrop-blur rounded-2xl px-6 py-4 flex items-center justify-between text-xs font-felix font-semibold text-stone-900 hover:bg-white/70 transition-all cursor-pointer border border-white/60"><span class="tracking-wide uppercase">Raw Whipped Shea &amp; Botanical Oils</span><span class="material-symbols-outlined text-[16px]">arrow_forward</span></div><div class="bg-white/50 backdrop-blur rounded-2xl px-6 py-4 flex items-center justify-between text-xs font-felix font-semibold text-stone-900 hover:bg-white/70 transition-all cursor-pointer border border-white/60"><span class="tracking-wide uppercase">Cruelty-Free &amp; Ethically Sourced</span><span class="material-symbols-outlined text-[16px]">arrow_forward</span></div></div></div></div></div></section>
<!-- ============================================== -->
<!-- 5. "IT'S TIME TO UPGRADE YOUR SKINCARE" SPLIT SECTION -->
<!-- ============================================== -->
<section class="w-full bg-white py-20 sm:py-28"><div class="max-w-7xl mx-auto px-6 sm:px-12"><span class="text-[11px] font-felix font-bold uppercase tracking-[0.2em] text-stone-400 block mb-8">Client Reviews • Real Results</span><div class="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center"><div class="lg:col-span-5 flex flex-col items-start space-y-4"><div class="flex items-center gap-2"></div><div class="relative w-full max-w-sm rounded-2xl overflow-hidden shadow-lg border border-stone-200"><img loading="lazy" decoding="async" alt="Portrait of Sara Jahan" class="w-full h-80 object-cover object-top" src="https://lh3.googleusercontent.com/aida-public/AB6AXuC-FaszPzHCNzDz_etx4EpBCEFGClC0gc7T4aFEBM6r4mhsuTTcGHv3Oow14qwVL7L7idi6dkybjvmySGKxogu4b7jLItOFuUz0afaXIx5JiBUNGNDpeVAu-msDjMYqxTUHQD0jV0BIgBWZCt6v_RSLDp6da6AEZpRB8TURX8w8JJJ0NA-Vs-K_UCvS0qo_Sx2fxLbrhiXPk-ST521DQDV5n6V7R3RRKz0ZlBtfXA"/><div class="p-3.5 bg-[#fcf9f9] flex items-center justify-between text-[11px] text-stone-700 font-medium"><span class="font-felix tracking-wide uppercase font-semibold">Happy Client</span><span class="text-stone-400">Est. 2018</span></div></div></div><div class="lg:col-span-7 flex flex-col justify-between space-y-8"><div><span class="text-6xl font-sinfonietta text-stone-900 block leading-none select-none">“</span><blockquote class="text-2xl sm:text-4xl font-felix font-normal text-stone-900 leading-snug mt-2">My hair has never felt so strong, and my skin feels deeply hydrated without irritation. Knowing it is free from sulphates and parabens gives me so much confidence.</blockquote><p class="text-xs text-stone-500 font-felix tracking-widest uppercase font-semibold mt-6">— Sara J., Loyal Customer since 2019</p></div><div class="pt-6 border-t border-stone-100 flex items-center justify-between"><div class="flex items-center gap-3"><div class="flex -space-x-2"><img loading="lazy" decoding="async" alt="By Nzuri product" class="w-8 h-8 rounded-full border-2 border-white object-cover shadow-sm" src="/images/products/exfoliatingtoner.webp"/><img loading="lazy" decoding="async" alt="By Nzuri product" class="w-8 h-8 rounded-full border-2 border-white object-cover shadow-sm" src="/images/products/growthelixir.webp"/><span class="w-8 h-8 rounded-full bg-[#111111] text-[#dcbec3] text-[10px] font-bold flex items-center justify-center border-2 border-white shadow-sm">+2k</span></div><div class="text-[11px] text-stone-600 leading-tight">They trusted by Nzuri for hair &amp; skin wellness.<br/>Ready whenever you are.</div></div></div></div></div></div></section>
<!-- ============================================== -->
<!-- 6. CUSTOMER REVIEWS / TESTIMONIAL SECTION -->
<!-- ============================================== -->

<!-- ============================================== -->
<!-- 7. "SKIN CARE TIPS & TRENDS" BLOG / ARTICLE ROW -->
<!-- ============================================== -->
<section class="final-cta" aria-labelledby="cta-title"><div class="cta-inner"><div class="cta-copy"><p class="cta-eyebrow">A little care, every day</p><h2 id="cta-title">Your care journey<br/><em>starts here.</em></h2><p class="cta-description">Give your hair and skin the attention they deserve. Discover your next everyday essential with By Nzuri.</p><router-link to="/catalog" class="cta-button">Explore the collection <span aria-hidden="true">↗</span></router-link></div><div class="cta-visual" aria-hidden="true"><div class="cta-halo"></div><span class="cta-watermark">NZURI</span><img src="/images/products/growthelixir.webp" alt="" loading="lazy"/><span class="cta-caption">Made for your<br/>everyday routine</span></div></div></section>

</div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Great+Vibes&family=Public+Sans:wght@300;400;500;600;700&family=Material+Symbols+Outlined&display=swap');
.stitch-landing { font-family: 'Public Sans', sans-serif; background: white; color: #1d1b20; }
.font-felix { font-family: 'Cinzel', serif; letter-spacing: .08em; }
.font-sinfonietta { font-family: 'Great Vibes', cursive; font-weight: 400; letter-spacing: .02em; }
.font-headline { font-family: 'Public Sans', sans-serif; }
.material-symbols-outlined { font-family: 'Material Symbols Outlined'; font-weight: normal; font-style: normal; display: inline-block; line-height: 1; letter-spacing: normal; text-transform: none; white-space: nowrap; word-wrap: normal; direction: ltr; -webkit-font-feature-settings: 'liga'; -webkit-font-smoothing: antialiased; }

.final-cta{background:#e8d2d4;overflow:hidden}.cta-inner{max-width:1280px;margin:auto;min-height:480px;padding:72px 48px;display:grid;grid-template-columns:1fr 1fr;align-items:center;gap:40px}.cta-copy{position:relative;z-index:1}.cta-eyebrow{display:flex;align-items:center;gap:10px;margin-bottom:24px;font:600 10px Cinzel,serif;letter-spacing:.18em;text-transform:uppercase}.cta-eyebrow:before{content:"";width:30px;height:1px;background:#292121}.final-cta h2{margin:0;color:#211d1c;font:400 clamp(2.8rem,5vw,4.8rem)/1.08 Cinzel,serif;letter-spacing:-.035em}.final-cta h2 em{font:400 1.35em/.9 'Great Vibes',cursive;letter-spacing:0}.cta-description{max-width:360px;margin:24px 0 30px;color:#5d5050;font-size:14px;line-height:1.8}.cta-button{display:inline-flex;align-items:center;gap:36px;padding:17px 23px;border-radius:999px;background:#171414;color:white;font:600 10px Cinzel,serif;letter-spacing:.12em;text-transform:uppercase;transition:background .2s,transform .2s}.cta-button:hover{background:#403334;transform:translateY(-2px)}.cta-button:focus-visible{outline:3px solid #6a4045;outline-offset:4px}.cta-button span{font:18px sans-serif}.cta-visual{min-height:350px;position:relative;display:grid;place-items:center}.cta-halo{position:absolute;width:min(90%,370px);aspect-ratio:1;border:1px solid rgba(80,49,50,.25);border-radius:50%;background:rgba(255,255,255,.2)}.cta-visual img{position:relative;z-index:1;height:350px;max-width:90%;object-fit:contain;filter:drop-shadow(0 18px 20px rgba(62,38,40,.15))}.cta-watermark{position:absolute;color:rgba(255,255,255,.35);font:600 clamp(4rem,10vw,9rem) Cinzel,serif;letter-spacing:.08em}.cta-caption{position:absolute;z-index:2;right:0;bottom:14%;color:#554044;font:400 11px/1.5 Cinzel,serif;letter-spacing:.09em;text-transform:uppercase}@media(max-width:700px){.cta-inner{grid-template-columns:1fr;padding:64px 24px 40px;gap:10px}.cta-visual{min-height:280px}.cta-visual img{height:280px}.cta-caption{right:2%}}@media(prefers-reduced-motion:reduce){.cta-button{transition:none}}

@media (max-width: 700px) {
  .cta-inner { min-height: 0; padding: 48px 24px 36px; gap: 24px; }
  .cta-eyebrow { margin-bottom: 18px; font-size: .625rem; }
  .final-cta h2 { font-size: clamp(2.1rem, 9vw, 2.7rem); line-height: 1.1; }
  .cta-description { margin: 18px 0 22px; font-size: .9375rem; line-height: 1.65; }
  .cta-button { min-height: 48px; gap: 24px; font-size: .6875rem; }
  .cta-visual { min-height: 280px; padding-bottom: 28px; }
  .cta-halo { width: min(78%, 250px); top: 0; }
  .cta-visual img { height: 240px; }
  .cta-watermark { font-size: clamp(4rem, 18vw, 6rem); top: 25%; }
  .cta-caption { right: 0; bottom: 0; font-size: .625rem; }
}
</style>
