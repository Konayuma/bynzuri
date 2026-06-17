<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useProductStore } from '@/stores/product'
import { ArrowRight } from '@lucide/vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import ProductCard from '@/components/product/ProductCard.vue'
import BaseButton from '@/components/base/BaseButton.vue'

gsap.registerPlugin(ScrollTrigger)

const productStore = useProductStore()

const heroRef = ref<HTMLElement | null>(null)
const categoriesRef = ref<HTMLElement | null>(null)
const bestSellersRef = ref<HTMLElement | null>(null)
const newArrivalsRef = ref<HTMLElement | null>(null)
const testimonialsRef = ref<HTMLElement | null>(null)
const newsletterRef = ref<HTMLElement | null>(null)

const newsletterEmail = ref('')
const newsletterSubscribed = ref(false)

function handleNewsletter() {
  if (newsletterEmail.value.trim()) {
    localStorage.setItem('bynzuri_newsletter', newsletterEmail.value.trim())
    newsletterSubscribed.value = true
    newsletterEmail.value = ''
  }
}

let ctx: gsap.Context | null = null

onMounted(() => {
  productStore.fetchBestSellers()
  productStore.fetchNewArrivals()
  productStore.fetchCategories()

  ctx = gsap.context(() => {
    if (heroRef.value) {
      gsap.fromTo(
        heroRef.value.querySelectorAll('.hero-animate'),
        { opacity: 0, y: 40 },
        { opacity: 1, y: 0, duration: 0.8, stagger: 0.15, ease: 'power2.out' }
      )
    }

    const sections = [
      { ref: categoriesRef, from: { y: 50 } },
      { ref: bestSellersRef, from: { y: 50 } },
      { ref: newArrivalsRef, from: { y: 50 } },
      { ref: testimonialsRef, from: { y: 40 } },
      { ref: newsletterRef, from: { y: 30 } }
    ]

    sections.forEach(({ ref: sectionRef, from }) => {
      if (!sectionRef.value) return
      ScrollTrigger.create({
        trigger: sectionRef.value,
        start: 'top 85%',
        onEnter: () => {
          gsap.fromTo(
            sectionRef.value!.querySelectorAll('.section-animate'),
            { opacity: 0, y: from.y },
            { opacity: 1, y: 0, duration: 0.7, stagger: 0.1, ease: 'power2.out' }
          )
        },
        once: true
      })
    })
  })
})

onUnmounted(() => {
  ctx?.revert()
})
</script>

<template>
  <div>
    <!-- Hero Banner -->
    <section ref="heroRef" class="relative min-h-[85vh] flex items-center bg-gradient-to-b from-primary/30 to-background overflow-hidden">
      <div class="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=1200')] bg-cover bg-center opacity-10" />
      <div class="max-w-7xl mx-auto px-4 py-20 w-full">
        <div class="max-w-xl">
          <p class="hero-animate text-sm text-gold uppercase tracking-[0.2em] font-medium mb-4">Premium Beauty &amp; Haircare</p>
          <h1 class="hero-animate font-heading text-4xl md:text-5xl lg:text-6xl font-bold text-dark leading-tight mb-6">
            Healthy Hair.<br />
            <span class="text-gold">Beautiful Confidence.</span><br />
            Delivered Across Zambia.
          </h1>
          <p class="hero-animate text-muted text-base md:text-lg mb-8 max-w-md leading-relaxed">
            Discover premium beauty essentials crafted for African hair. Quality products, trusted by women across Zambia.
          </p>
          <div class="hero-animate flex flex-col sm:flex-row gap-3">
            <router-link to="/catalog">
              <BaseButton variant="secondary" size="md">
                Shop Now
                <ArrowRight class="w-4 h-4 ml-2" />
              </BaseButton>
            </router-link>
            <router-link to="/catalog">
              <BaseButton variant="outline" size="md">
                Browse Collections
              </BaseButton>
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Trust Bar -->
    <section class="border-y border-primary/20">
      <div class="max-w-7xl mx-auto px-4 py-4">
        <div class="flex flex-wrap items-center justify-center gap-6 md:gap-12 text-xs text-muted font-medium">
          <span class="flex items-center gap-2">
            <span class="w-1.5 h-1.5 rounded-full bg-success" />
            Secure Payments
          </span>
          <span class="flex items-center gap-2">
            <span class="w-1.5 h-1.5 rounded-full bg-gold" />
            Nationwide Delivery
          </span>
          <span class="flex items-center gap-2">
            <span class="w-1.5 h-1.5 rounded-full bg-primary" />
            Verified Products
          </span>
          <span class="flex items-center gap-2">
            <span class="w-1.5 h-1.5 rounded-full bg-dark" />
            Loved by Thousands
          </span>
        </div>
      </div>
    </section>

    <!-- Featured Categories -->
    <section ref="categoriesRef" class="max-w-7xl mx-auto px-4 py-16 md:py-20">
      <div class="flex items-end justify-between mb-8">
        <div>
          <p class="section-animate text-xs text-gold uppercase tracking-[0.2em] font-medium mb-2">Categories</p>
          <h2 class="section-animate font-heading text-2xl md:text-3xl font-semibold text-dark">Shop by Category</h2>
        </div>
        <router-link to="/catalog" class="section-animate hidden sm:flex items-center gap-1 text-sm text-muted hover:text-dark transition-colors">
          View All <ArrowRight class="w-3.5 h-3.5" />
        </router-link>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 md:gap-4">
        <router-link
          v-for="(cat, i) in productStore.categories.slice(0, 6)"
          :key="cat.id"
          :to="`/catalog?category=${cat.slug}`"
          :style="{ transitionDelay: `${i * 0.05}s` }"
          class="section-animate group relative aspect-square rounded-[20px] overflow-hidden bg-primary/20"
        >
          <img
            v-if="cat.image"
            :src="cat.image"
            :alt="cat.name"
            class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            loading="lazy"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
          <div class="absolute bottom-0 left-0 right-0 p-3">
            <h3 class="text-white text-sm font-medium">{{ cat.name }}</h3>
          </div>
        </router-link>

        <template v-if="productStore.categories.length === 0">
          <div v-for="i in 6" :key="i" class="aspect-square rounded-[20px] bg-primary/30 animate-pulse" />
        </template>
      </div>
    </section>

    <!-- Best Sellers -->
    <section ref="bestSellersRef" class="max-w-7xl mx-auto px-4 py-16 md:py-20">
      <div class="flex items-end justify-between mb-8">
        <div>
          <p class="section-animate text-xs text-gold uppercase tracking-[0.2em] font-medium mb-2">Best Sellers</p>
          <h2 class="section-animate font-heading text-2xl md:text-3xl font-semibold text-dark">Most Loved Products</h2>
        </div>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
        <ProductCard
          v-for="product in productStore.bestSellers"
          :key="product.id"
          :product="product"
          class="section-animate"
        />
        <template v-if="productStore.bestSellers.length === 0">
          <div v-for="i in 4" :key="i" class="section-animate space-y-3">
            <div class="aspect-[3/4] rounded-[20px] bg-primary/30 animate-pulse" />
            <div class="h-3 w-16 bg-primary/30 rounded animate-pulse" />
            <div class="h-4 w-32 bg-primary/30 rounded animate-pulse" />
            <div class="h-4 w-20 bg-primary/30 rounded animate-pulse" />
          </div>
        </template>
      </div>
    </section>

    <!-- New Arrivals -->
    <section ref="newArrivalsRef" class="bg-primary/20 py-16 md:py-20">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex items-end justify-between mb-8">
          <div>
            <p class="section-animate text-xs text-gold uppercase tracking-[0.2em] font-medium mb-2">New In</p>
            <h2 class="section-animate font-heading text-2xl md:text-3xl font-semibold text-dark">New Arrivals</h2>
          </div>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
          <ProductCard
            v-for="product in productStore.newArrivals"
            :key="product.id"
            :product="product"
            class="section-animate"
          />
          <template v-if="productStore.newArrivals.length === 0">
            <div v-for="i in 4" :key="i" class="section-animate space-y-3">
              <div class="aspect-[3/4] rounded-[20px] bg-background/50 animate-pulse" />
              <div class="h-3 w-16 bg-background/50 rounded animate-pulse" />
              <div class="h-4 w-32 bg-background/50 rounded animate-pulse" />
              <div class="h-4 w-20 bg-background/50 rounded animate-pulse" />
            </div>
          </template>
        </div>
      </div>
    </section>

    <!-- Testimonials -->
    <section ref="testimonialsRef" class="max-w-7xl mx-auto px-4 py-16 md:py-20">
      <div class="text-center mb-10">
        <p class="section-animate text-xs text-gold uppercase tracking-[0.2em] font-medium mb-2">Testimonials</p>
        <h2 class="section-animate font-heading text-2xl md:text-3xl font-semibold text-dark">Loved By Women Across Zambia</h2>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div
          v-for="(testimonial, i) in testimonials"
          :key="i"
          :style="{ transitionDelay: `${i * 0.1}s` }"
          class="section-animate bg-white p-6 rounded-[20px] shadow-[0_8px_30px_rgba(0,0,0,0.06)] hover:shadow-[0_12px_40px_rgba(0,0,0,0.1)] transition-shadow duration-300"
        >
          <div class="flex items-center gap-1 mb-3">
            <svg v-for="s in 5" :key="s" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="#C7A46A" stroke="#C7A46A" stroke-width="1"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          </div>
          <p class="text-sm text-muted leading-relaxed mb-4">&ldquo;{{ testimonial.text }}&rdquo;</p>
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-primary/40 flex-shrink-0" />
            <div>
              <p class="text-sm font-medium text-dark">{{ testimonial.name }}</p>
              <p class="text-xs text-muted">{{ testimonial.location }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Instagram Section -->
    <section class="bg-dark/5 py-16 md:py-20">
      <div class="max-w-7xl mx-auto px-4">
        <div class="text-center mb-8">
          <p class="section-animate text-xs text-gold uppercase tracking-[0.2em] font-medium mb-2">Follow Us</p>
          <h2 class="section-animate font-heading text-2xl md:text-3xl font-semibold text-dark">@bynzuri</h2>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-3">
          <div v-for="i in 4" :key="i" class="aspect-square rounded-[14px] bg-primary/30 overflow-hidden group cursor-pointer">
            <div class="w-full h-full bg-gradient-to-br from-primary/40 to-gold/20 flex items-center justify-center transition-transform duration-300 group-hover:scale-105">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="text-muted group-hover:text-gold transition-colors duration-300"><rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/></svg>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Newsletter -->
    <section ref="newsletterRef" class="max-w-2xl mx-auto px-4 py-16 md:py-20 text-center">
      <p class="section-animate text-xs text-gold uppercase tracking-[0.2em] font-medium mb-2">Stay Connected</p>
      <h2 class="section-animate font-heading text-2xl md:text-3xl font-semibold text-dark mb-3">Join the Beauty Circle</h2>
      <p class="section-animate text-muted text-sm mb-6">Be the first to know about new arrivals, exclusive offers, and beauty tips.</p>
      <div v-if="!newsletterSubscribed" class="section-animate flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
        <input
          v-model="newsletterEmail"
          type="email"
          placeholder="Enter your email"
          required
          class="flex-1 px-4 py-3 bg-white border border-primary/40 rounded-[14px] text-sm focus:outline-none focus:border-gold transition-colors"
        />
        <BaseButton variant="secondary" @click="handleNewsletter">
          Subscribe
        </BaseButton>
      </div>
      <p v-else class="section-animate text-sm text-success">Thanks for subscribing!</p>
    </section>
  </div>
</template>

<script lang="ts">
const testimonials = [
  {
    text: "By Nzuri has completely transformed my hair care routine. The growth oil is amazing — I've seen real results in just weeks.",
    name: "Chanda M.",
    location: "Lusaka"
  },
  {
    text: "The quality of their products is unmatched. Fast delivery in Lusaka too. I'm a customer for life!",
    name: "Mutale K.",
    location: "Kitwe"
  },
  {
    text: "Finally, a beauty brand that understands African hair. Beautiful products, beautiful packaging, beautiful results.",
    name: "Thandiwe B.",
    location: "Ndola"
  }
]
</script>
