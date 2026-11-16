<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useProductStore } from '@/stores/product'
import ProductCard from '@/components/product/ProductCard.vue'
import { useUIStore } from '@/stores/ui'
const router = useRouter()
const uiStore = useUIStore()
const productStore = useProductStore()
const productsError = ref(false)
const collection = [
  { name: 'Growth Elixir', image: 'growthelixir.png' },
  { name: 'Nourishing Oil Mix', image: 'nourishingoilmix.png' },
  { name: 'Shea Butter', image: 'sheabutter.png' },
  { name: 'Shampoo Bar', image: 'shampoobar.png' },
  { name: 'Deep Conditioner', image: 'deepconditioner.png' },
  { name: 'Leave-in Conditioner', image: 'leaveinconditioner.png' },
  { name: 'Herbal Hair Mist', image: 'herbalhairmist.png' },
  { name: 'Exfoliating Toner', image: 'exfoliatingtoner.png' },
]
onMounted(async () => {
  try { await productStore.fetchProducts() } catch { productsError.value = true }
})
</script>

<template>
<div class="stitch-landing">


<!-- 1. HERO SECTION WITH MINIMALIST HEADER & WARM AMBIENT GLOW -->
<!-- ============================================== -->
<header class="absolute top-0 left-0 right-0 z-50"><div class="max-w-7xl mx-auto px-6 sm:px-12 h-24 flex items-center justify-between text-stone-900"><a class="flex items-center gap-3.5 group" href="/catalog"><div class="w-11 h-11 rounded-full border border-stone-900 flex items-center justify-center text-[8px] font-felix tracking-widest text-center uppercase p-1 leading-none shadow-sm bg-white/80 backdrop-blur"><span>HAIR &amp; SKIN<br/><span class="text-[6px] tracking-normal">EST. 2018</span></span></div><div class="flex flex-col"><span class="text-xs font-felix tracking-[0.22em] uppercase font-bold text-stone-900">Hair &amp; Skincare</span><span class="text-2xl font-sinfonietta text-stone-900 -mt-1.5 leading-none">by Nzuri</span></div></a><nav class="hidden md:flex items-center gap-8 text-xs tracking-widest font-medium uppercase text-stone-700"><a class="text-stone-900 font-semibold hover:text-black transition-colors" href="/catalog">Home</a><a class="hover:text-black transition-colors" href="#about">About Us</a><a class="hover:text-black transition-colors flex items-center gap-1" href="#sellers">Hair Care <span class="text-stone-400">+</span></a><a class="hover:text-black transition-colors flex items-center gap-1" href="#sellers">Skin Care <span class="text-stone-400">+</span></a><a class="hover:text-black transition-colors" href="#contact">Contact</a></nav><div class="flex items-center gap-4 text-stone-800"><button @click="router.push('/catalog')" aria-label="Search" class="hover:text-black hover:scale-105 transition-all p-1.5 rounded-full hover:bg-black/5"><span class="material-symbols-outlined text-[20px]">search</span></button><button @click="router.push('/account')" aria-label="Account" class="hover:text-black hover:scale-105 transition-all p-1.5 rounded-full hover:bg-black/5"><span class="material-symbols-outlined text-[20px]">person</span></button><a @click.prevent="uiStore.openCart()" aria-label="Cart" class="hover:text-black hover:scale-105 transition-all p-1.5 rounded-full hover:bg-black/5 relative" href="#sellers"><span class="material-symbols-outlined text-[20px]">shopping_bag</span></a></div></div></header>
<section class="relative w-full min-h-[92vh] lg:min-h-screen bg-[#fcf9f9] overflow-hidden flex items-center pt-28 pb-16 border-b border-stone-200/60"><div class="pointer-events-none absolute top-14 left-1/2 -translate-x-1/2 w-full text-center z-0 overflow-hidden leading-none select-none opacity-[0.07]"><span class="text-[20vw] font-felix font-bold uppercase tracking-[0.25em] text-[#dcbec3] block">BY NZURI</span></div><div class="absolute -top-32 -left-32 w-96 h-96 rounded-full bg-[#dcbec3]/35 blur-3xl pointer-events-none"></div><div class="absolute bottom-0 right-0 w-[500px] h-[500px] rounded-full bg-[#dcbec3]/30 blur-3xl pointer-events-none"></div><div class="relative z-10 max-w-7xl mx-auto px-6 sm:px-12 w-full grid grid-cols-1 lg:grid-cols-12 gap-12 items-center"><div class="lg:col-span-6 text-stone-900 space-y-8"><div class="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-white border border-[#dcbec3] shadow-sm"><span class="w-2 h-2 rounded-full bg-[#111111]"></span><span class="text-[11px] font-felix tracking-widest uppercase text-stone-800 font-semibold">100% Organic &amp; Toxic-Free • Est. 2018</span></div><div class="space-y-3"><h1 class="text-4xl sm:text-5xl lg:text-6xl font-felix font-normal tracking-tight text-stone-900 leading-[1.15]">ELEVATE YOUR <br/><span class="font-sinfonietta text-5xl sm:text-6xl lg:text-7xl text-[#111111] block -mt-2">Hair &amp; Skincare Ritual</span></h1><p class="text-xs sm:text-sm text-stone-600 max-w-md font-light leading-relaxed pt-2">Formulated with nourishing raw botanicals and safe organic actives to ensure your hair and skin are completely free from sulphates, parabens, and mineral oils.</p></div><div class="flex flex-wrap items-center gap-4 pt-2"><a class="px-8 py-3.5 rounded-full bg-[#111111] text-white text-xs font-felix tracking-widest uppercase hover:bg-stone-800 transition-all shadow-md" href="#sellers">Shop The Collection</a><a class="px-8 py-3.5 rounded-full border border-stone-900 text-stone-900 text-xs font-felix tracking-widest uppercase hover:bg-[#dcbec3]/40 transition-all" href="#about">Our Story</a></div><div class="pt-4 flex flex-col sm:flex-row items-start sm:items-center gap-4 text-stone-700"><div class="flex -space-x-2"><img alt="By Nzuri product" class="w-8 h-8 rounded-full border-2 border-white object-cover shadow-sm" src="/images/products/growthelixir.png"/><img alt="By Nzuri product" class="w-8 h-8 rounded-full border-2 border-white object-cover shadow-sm" src="/images/products/sheabutter.png"/><img alt="By Nzuri product" class="w-8 h-8 rounded-full border-2 border-white object-cover shadow-sm" src="/images/products/nourishingoilmix.png"/></div><p class="text-xs text-stone-500 max-w-xs leading-relaxed font-light">Trusted by thousands since 2018 for holistic hair restoration &amp; radiant natural skin.</p></div></div><div class="lg:col-span-6 relative flex justify-center items-center"><div class="relative w-full max-w-md lg:max-w-lg"><div class="absolute -inset-4 bg-[#dcbec3] rounded-3xl filter blur-xl opacity-50 transform rotate-2"></div><img alt="By Nzuri product" class="relative z-10 w-full h-[470px] sm:h-[560px] object-cover object-top rounded-3xl shadow-2xl border-4 border-white" src="/images/products/herbalhairmist.png"/><div class="absolute -bottom-6 -left-6 z-20 bg-white p-4 rounded-2xl shadow-xl border border-stone-200/80 max-w-[200px]"><div class="flex items-center gap-2 mb-1"><span class="material-symbols-outlined text-[16px] text-stone-800">eco</span><span class="text-[10px] font-felix tracking-wider uppercase font-bold text-stone-900">Clean Beauty</span></div><p class="text-[11px] text-stone-500 leading-tight">No sulphates, parabens, or mineral oils.</p></div></div></div></div></section>
<!-- ============================================== -->
<!-- 2. "OUR BEST SELLERS" PRODUCT ROW -->
<!-- ============================================== -->
<section id="sellers" class="w-full bg-[#fbf9f8] py-20 sm:py-24">
  <div class="max-w-7xl mx-auto px-6 sm:px-12">
    <div class="flex flex-wrap items-end justify-between gap-4 mb-10">
      <div><span class="text-[11px] font-felix tracking-[0.2em] uppercase text-stone-500 block mb-2">Curated Formulations</span><h2 class="text-3xl sm:text-4xl font-felix text-stone-900">Our <span class="font-sinfonietta text-4xl sm:text-5xl">Signature</span> Collection</h2></div>
      <router-link to="/catalog" class="text-xs font-felix uppercase tracking-wider underline underline-offset-4">Shop all products</router-link>
    </div>
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
      <router-link v-for="item in collection" :key="item.image" :to="{ path: '/catalog', query: { search: item.name } }" class="group rounded-2xl bg-white p-4 sm:p-5 border border-stone-100 shadow-sm hover:shadow-md transition-shadow">
        <div class="aspect-square bg-[#fcf9f9] rounded-xl overflow-hidden flex items-center justify-center"><img :src="`/images/products/${item.image}`" :alt="item.name" class="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300" loading="lazy" /></div>
        <div class="flex justify-between items-center gap-2 pt-4"><h3 class="text-xs sm:text-sm font-felix font-semibold text-stone-900">{{ item.name }}</h3><span aria-hidden="true">↗</span></div>
      </router-link>
    </div>
  </div>
</section>
<section class="w-full bg-white py-20" aria-labelledby="shop-products-title">
  <div class="max-w-7xl mx-auto px-6 sm:px-12">
    <div class="flex flex-wrap items-end justify-between gap-4 mb-10"><div><span class="text-[11px] font-felix tracking-[0.2em] uppercase text-stone-500 block mb-2">The Nzuri Shop</span><h2 id="shop-products-title" class="text-3xl sm:text-4xl font-felix text-stone-900">Shop Our Products</h2></div><router-link to="/catalog" class="text-xs font-felix uppercase tracking-wider underline underline-offset-4">View all</router-link></div>
    <p v-if="productStore.loading" class="text-sm text-stone-500" role="status">Loading products…</p>
    <p v-else-if="productsError" class="text-sm text-stone-500">Products are temporarily unavailable. Please try again later.</p>
    <p v-else-if="!productStore.products.length" class="text-sm text-stone-500">There are no products available yet.</p>
    <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6"><ProductCard v-for="product in productStore.products.slice(0, 8)" :key="product.id" :product="product" /></div>
  </div>
</section>
<!-- ============================================== -->
<!-- 3. MISSION / STATEMENT CALLOUT SECTION (WARM SAND / CLAY) -->
<!-- ============================================== -->
<section class="relative w-full bg-[#dcbec3] py-24 sm:py-32 overflow-hidden text-center" id="about"><div class="pointer-events-none absolute inset-x-0 bottom-4 text-center z-0 select-none opacity-20 overflow-hidden"><span class="text-[18vw] font-felix font-bold uppercase tracking-[0.2em] text-white block">NZURI</span></div><div class="relative z-10 max-w-4xl mx-auto px-6 sm:px-12 flex flex-col items-center"><div class="inline-block px-4 py-1.5 rounded-full bg-white/70 border border-white text-[11px] font-felix font-semibold uppercase tracking-[0.25em] text-stone-800 mb-6">Our Brand Story • Founded 2018</div><h2 class="text-2xl sm:text-4xl lg:text-5xl font-felix font-normal text-stone-900 leading-tight max-w-3xl mb-6">HAIR AND SKINCARE BY NZURI IS DEDICATED TO <span class="font-sinfonietta text-4xl sm:text-5xl lg:text-6xl text-stone-950 block mt-1">Safe Organic Formulations</span></h2><p class="text-sm sm:text-base text-stone-800 max-w-2xl font-light leading-relaxed mb-10">We create beauty essentials crafted from raw, natural ingredients with the aim of ensuring your hair and skin are completely free from toxic chemicals such as sulphates, parabens, and mineral oils.</p><div class="grid grid-cols-2 sm:grid-cols-4 gap-4 w-full max-w-2xl mb-12"><div class="p-3 bg-white/80 rounded-xl shadow-sm border border-white/60"><span class="text-xs font-felix font-bold text-stone-900 block">SULPHATE-FREE</span><span class="text-[10px] text-stone-600">Gentle cleansing</span></div><div class="p-3 bg-white/80 rounded-xl shadow-sm border border-white/60"><span class="text-xs font-felix font-bold text-stone-900 block">PARABEN-FREE</span><span class="text-[10px] text-stone-600">Zero toxins</span></div><div class="p-3 bg-white/80 rounded-xl shadow-sm border border-white/60"><span class="text-xs font-felix font-bold text-stone-900 block">NO MINERAL OIL</span><span class="text-[10px] text-stone-600">Pure botanicals</span></div><div class="p-3 bg-white/80 rounded-xl shadow-sm border border-white/60"><span class="text-xs font-felix font-bold text-stone-900 block">100% ORGANIC</span><span class="text-[10px] text-stone-600">Sustainably crafted</span></div></div><div class="relative transform rotate-1 hover:rotate-0 transition-transform duration-500 shadow-2xl rounded-2xl overflow-hidden max-w-sm sm:max-w-md border-4 border-white"><img alt="Hair and Skincare by Nzuri product line" class="w-full h-80 sm:h-96 object-cover" src="/images/products/deepconditioner.png"/></div></div></section>
<!-- ============================================== -->
<!-- 4. "OUR KEY ADVANTAGES" TRUST ROW -->
<!-- ============================================== -->
<section class="w-full bg-[#fcf9f9] py-16 sm:py-24"><div class="max-w-7xl mx-auto px-6 sm:px-12"><div class="rounded-3xl overflow-hidden grid grid-cols-1 lg:grid-cols-12 shadow-xl border border-stone-200/80"><div class="lg:col-span-6 relative min-h-[460px] lg:min-h-full"><img alt="By Nzuri product" class="absolute inset-0 w-full h-full object-cover" src="/images/products/shampoobar.png"/></div><div class="lg:col-span-6 bg-[#dcbec3] p-8 sm:p-14 text-stone-900 flex flex-col justify-center"><div class="mb-8"><span class="text-[11px] font-felix tracking-[0.2em] uppercase font-bold text-stone-800 block mb-2">Pure Hair &amp; Skin Wellness</span><h2 class="text-3xl sm:text-4xl font-felix font-normal text-stone-900 leading-tight">It's Time to <span class="font-sinfonietta text-4xl sm:text-5xl text-stone-950 block mt-1">Upgrade Your Routine</span></h2><p class="text-xs text-stone-700 font-light mt-3 leading-relaxed">Handcrafted with certified organic botanical oils, soothing hydrators, and nutrient-dense raw butters to give lasting radiance.</p></div><div class="space-y-3.5"><div class="bg-white rounded-2xl p-6 text-stone-900 shadow-md border border-white"><h3 class="text-sm font-felix font-bold mb-2 uppercase tracking-wide">Organic &amp; Toxic-Free Ingredients</h3><p class="text-xs text-stone-600 leading-relaxed font-light mb-4">Formulated free from parabens, harsh sulphates, and synthetic fillers for healthy scalp stimulation and hydrated, supple skin.</p><a class="text-xs font-felix font-bold text-stone-900 underline hover:text-stone-700 tracking-wider uppercase" href="#sellers">Explore All Formulations →</a></div><div class="bg-white/50 backdrop-blur rounded-2xl px-6 py-4 flex items-center justify-between text-xs font-felix font-semibold text-stone-900 hover:bg-white/70 transition-all cursor-pointer border border-white/60"><span class="tracking-wide uppercase">Nourishing Scalp &amp; Follicle Care</span><span class="material-symbols-outlined text-[16px]">arrow_forward</span></div><div class="bg-white/50 backdrop-blur rounded-2xl px-6 py-4 flex items-center justify-between text-xs font-felix font-semibold text-stone-900 hover:bg-white/70 transition-all cursor-pointer border border-white/60"><span class="tracking-wide uppercase">Raw Whipped Shea &amp; Botanical Oils</span><span class="material-symbols-outlined text-[16px]">arrow_forward</span></div><div class="bg-white/50 backdrop-blur rounded-2xl px-6 py-4 flex items-center justify-between text-xs font-felix font-semibold text-stone-900 hover:bg-white/70 transition-all cursor-pointer border border-white/60"><span class="tracking-wide uppercase">Cruelty-Free &amp; Ethically Sourced</span><span class="material-symbols-outlined text-[16px]">arrow_forward</span></div></div></div></div></div></section>
<!-- ============================================== -->
<!-- 5. "IT'S TIME TO UPGRADE YOUR SKINCARE" SPLIT SECTION -->
<!-- ============================================== -->
<section class="w-full bg-white py-20 sm:py-28"><div class="max-w-7xl mx-auto px-6 sm:px-12"><span class="text-[11px] font-felix font-bold uppercase tracking-[0.2em] text-stone-400 block mb-8">Client Reviews • Real Results</span><div class="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center"><div class="lg:col-span-5 flex flex-col items-start space-y-4"><div class="flex items-center gap-2"></div><div class="relative w-full max-w-sm rounded-2xl overflow-hidden shadow-lg border border-stone-200"><img alt="Portrait of Sara Jahan" class="w-full h-80 object-cover object-top" src="https://lh3.googleusercontent.com/aida-public/AB6AXuC-FaszPzHCNzDz_etx4EpBCEFGClC0gc7T4aFEBM6r4mhsuTTcGHv3Oow14qwVL7L7idi6dkybjvmySGKxogu4b7jLItOFuUz0afaXIx5JiBUNGNDpeVAu-msDjMYqxTUHQD0jV0BIgBWZCt6v_RSLDp6da6AEZpRB8TURX8w8JJJ0NA-Vs-K_UCvS0qo_Sx2fxLbrhiXPk-ST521DQDV5n6V7R3RRKz0ZlBtfXA"/><div class="p-3.5 bg-[#fcf9f9] flex items-center justify-between text-[11px] text-stone-700 font-medium"><span class="font-felix tracking-wide uppercase font-semibold">Happy Client</span><span class="text-stone-400">Est. 2018</span></div></div></div><div class="lg:col-span-7 flex flex-col justify-between space-y-8"><div><span class="text-6xl font-sinfonietta text-stone-900 block leading-none select-none">“</span><blockquote class="text-2xl sm:text-4xl font-felix font-normal text-stone-900 leading-snug mt-2">My hair has never felt so strong, and my skin feels deeply hydrated without irritation. Knowing it is free from sulphates and parabens gives me so much confidence.</blockquote><p class="text-xs text-stone-500 font-felix tracking-widest uppercase font-semibold mt-6">— Sara J., Loyal Customer since 2019</p></div><div class="pt-6 border-t border-stone-100 flex items-center justify-between"><div class="flex items-center gap-3"><div class="flex -space-x-2"><img alt="By Nzuri product" class="w-8 h-8 rounded-full border-2 border-white object-cover shadow-sm" src="/images/products/exfoliatingtoner.png"/><img alt="By Nzuri product" class="w-8 h-8 rounded-full border-2 border-white object-cover shadow-sm" src="/images/products/growthelixir.png"/><span class="w-8 h-8 rounded-full bg-[#111111] text-[#dcbec3] text-[10px] font-bold flex items-center justify-center border-2 border-white shadow-sm">+2k</span></div><div class="text-[11px] text-stone-600 leading-tight">They trusted by Nzuri for hair &amp; skin wellness.<br/>Ready whenever you are.</div></div></div></div></div></div></section>
<!-- ============================================== -->
<!-- 6. CUSTOMER REVIEWS / TESTIMONIAL SECTION -->
<!-- ============================================== -->

<!-- ============================================== -->
<!-- 7. "SKIN CARE TIPS & TRENDS" BLOG / ARTICLE ROW -->
<!-- ============================================== -->
<section class="w-full bg-[#fbf9f8] py-20 sm:py-28">
<div class="max-w-7xl mx-auto px-6 sm:px-12">
<div class="text-center mb-14">
<h2 class="text-3xl sm:text-4xl font-headline font-semibold text-[#1f1a17]">
        Skin Care <span class="font-serif-italic font-normal">Tips &amp; Trends</span>
</h2>
</div>
<!-- 3 Clean Editorial Cards -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
<!-- Article 1 -->
<article class="bg-white rounded-2xl p-4 shadow-sm hover:shadow-md transition-shadow group flex flex-col justify-between">
<div class="relative w-full h-52 rounded-xl overflow-hidden mb-4">
<img alt="By Nzuri product" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" src="/images/products/deepconditioner.png"/>
<a class="absolute top-3 right-3 w-8 h-8 rounded-full bg-white/90 backdrop-blur text-stone-800 flex items-center justify-center shadow-sm group-hover:bg-[#af6f4a] group-hover:text-white transition-colors" href="/catalog">
<span class="material-symbols-outlined text-[16px]">north_east</span>
</a>
</div>
<div>
<div class="flex items-center gap-3 text-[10px] text-stone-400 mb-2">
<span>October 10, 2026</span>
<span>•</span>
<span>3 min read</span>
</div>
<h3 class="text-sm font-bold text-stone-800 group-hover:text-[#af6f4a] transition-colors leading-snug">
            Why Gentle Formulations Are Better for Your Skin Every Day
          </h3>
</div>
</article>
<!-- Article 2 -->
<article class="bg-white rounded-2xl p-4 shadow-sm hover:shadow-md transition-shadow group flex flex-col justify-between">
<div class="relative w-full h-52 rounded-xl overflow-hidden mb-4">
<img alt="By Nzuri product" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" src="/images/products/shampoobar.png"/>
<a class="absolute top-3 right-3 w-8 h-8 rounded-full bg-white/90 backdrop-blur text-stone-800 flex items-center justify-center shadow-sm group-hover:bg-[#af6f4a] group-hover:text-white transition-colors" href="/catalog">
<span class="material-symbols-outlined text-[16px]">north_east</span>
</a>
</div>
<div>
<div class="flex items-center gap-3 text-[10px] text-stone-400 mb-2">
<span>October 10, 2026</span>
<span>•</span>
<span>3 min read</span>
</div>
<h3 class="text-sm font-bold text-stone-800 group-hover:text-[#af6f4a] transition-colors leading-snug">
            Why Gentle Deodorants Are Better for Your Skin Every Day
          </h3>
</div>
</article>
<!-- Article 3 -->
<article class="bg-white rounded-2xl p-4 shadow-sm hover:shadow-md transition-shadow group flex flex-col justify-between">
<div class="relative w-full h-52 rounded-xl overflow-hidden mb-4">
<img alt="By Nzuri product" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" src="/images/products/leaveinconditioner.png"/>
<a class="absolute top-3 right-3 w-8 h-8 rounded-full bg-white/90 backdrop-blur text-stone-800 flex items-center justify-center shadow-sm group-hover:bg-[#af6f4a] group-hover:text-white transition-colors" href="/catalog">
<span class="material-symbols-outlined text-[16px]">north_east</span>
</a>
</div>
<div>
<div class="flex items-center gap-3 text-[10px] text-stone-400 mb-2">
<span>October 10, 2026</span>
<span>•</span>
<span>3 min read</span>
</div>
<h3 class="text-sm font-bold text-stone-800 group-hover:text-[#af6f4a] transition-colors leading-snug">
            Simple Evening Practices to Maintain Dewy Barrier Moisture
          </h3>
</div>
</article>
</div>
<!-- Centered Button -->
<div class="text-center">
<a class="inline-block px-7 py-3 rounded-full bg-[#af6f4a] hover:bg-[#8a4f32] text-white text-xs font-semibold tracking-wide transition-colors" href="/catalog">
        View all Article
      </a>
</div>
</div>
</section>
<!-- ============================================== -->
<!-- 8. STREAMLINED FOOTER (RICH WARM TERRACOTTA / SAND TONE) -->
<!-- ============================================== -->
<footer class="relative w-full bg-[#111111] text-white/90 pt-16 pb-12 overflow-hidden border-t border-stone-800" id="contact"><div class="max-w-7xl mx-auto px-6 sm:px-12 relative z-10"><div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-10 pb-16"><div class="lg:col-span-4 space-y-4"><div class="flex items-center gap-3"><div class="w-10 h-10 rounded-full border border-[#dcbec3] flex items-center justify-center text-[7px] font-felix tracking-widest text-[#dcbec3] uppercase p-1 leading-none"><span>NZURI<br/>2018</span></div><div><span class="text-xs font-felix tracking-[0.2em] uppercase font-bold text-white block">Hair &amp; Skincare</span><span class="text-xl font-sinfonietta text-[#dcbec3] leading-none block -mt-1">by Nzuri</span></div></div><p class="text-xs text-stone-400 font-light leading-relaxed max-w-sm">A clean beauty brand dedicated to formulating hair and skincare made with safe organic botanicals. Free from sulphates, parabens, and mineral oils. Founded in 2018.</p></div><div class="lg:col-span-2 space-y-3"><h4 class="text-xs font-felix font-bold tracking-widest uppercase text-[#dcbec3]">Quick Links</h4><ul class="space-y-2 text-xs text-stone-400 font-light"><li><a class="hover:text-white transition-colors" href="/catalog">Home</a></li><li><a class="hover:text-white transition-colors" href="#about">About Us</a></li><li><a class="hover:text-white transition-colors" href="#sellers">Hair Care</a></li><li><a class="hover:text-white transition-colors" href="#sellers">Skin Care</a></li><li><a class="hover:text-white transition-colors" href="#contact">Contact</a></li></ul></div><div class="lg:col-span-2 space-y-3"><h4 class="text-xs font-felix font-bold tracking-widest uppercase text-[#dcbec3]">Customer Care</h4><ul class="space-y-2 text-xs text-stone-400 font-light"><li><a class="hover:text-white transition-colors" href="/catalog">Shipping &amp; Delivery</a></li><li><a class="hover:text-white transition-colors" href="/catalog">Returns &amp; Refunds</a></li><li><a class="hover:text-white transition-colors" href="/catalog">Ingredients Glossary</a></li><li><a class="hover:text-white transition-colors" href="/catalog">Clean Standards</a></li></ul></div><div class="lg:col-span-4 space-y-3"><h4 class="text-xs font-felix font-bold tracking-widest uppercase text-[#dcbec3]">Join The Nzuri Circle</h4><p class="text-xs text-stone-400 font-light">Receive exclusive clean beauty tips and member-only releases.</p><router-link to="/help" class="text-xs underline">Contact us</router-link></div></div><div class="pt-8 border-t border-stone-800 flex flex-col sm:flex-row items-center justify-between text-xs text-stone-500 font-light gap-4"><p>© 2018–2026 Hair and Skincare by Nzuri. All rights reserved.</p><div class="flex items-center gap-6"><a class="hover:text-stone-300 transition-colors" href="/catalog">Terms &amp; Conditions</a><a class="hover:text-stone-300 transition-colors" href="/catalog">Privacy Policy</a></div></div></div><div class="pointer-events-none absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/3 w-full text-center z-0 overflow-hidden leading-none select-none opacity-[0.04]"><span class="text-[20vw] font-felix font-bold uppercase tracking-[0.25em] text-[#dcbec3] block">BY NZURI</span></div></footer>

</div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Great+Vibes&family=Public+Sans:wght@300;400;500;600;700&family=Material+Symbols+Outlined&display=swap');
.stitch-landing { font-family: 'Public Sans', sans-serif; background: white; color: #1d1b20; }
.font-felix { font-family: 'Cinzel', serif; letter-spacing: .08em; }
.font-sinfonietta { font-family: 'Great Vibes', cursive; font-weight: 400; letter-spacing: .02em; }
.font-headline { font-family: 'Public Sans', sans-serif; }
.material-symbols-outlined { font-family: 'Material Symbols Outlined'; font-weight: normal; font-style: normal; display: inline-block; line-height: 1; letter-spacing: normal; text-transform: none; white-space: nowrap; word-wrap: normal; direction: ltr; -webkit-font-feature-settings: 'liga'; -webkit-font-smoothing: antialiased; }
</style>
