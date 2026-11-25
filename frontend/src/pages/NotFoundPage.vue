<script setup lang="ts">
import { onMounted, ref } from 'vue'

interface NetworkInformation {
  saveData?: boolean
  effectiveType?: string
}

const shouldPlayVideo = ref(false)
const videoReady = ref(false)

onMounted(() => {
  const prefersReducedMotion =
    typeof window !== 'undefined' &&
    typeof window.matchMedia === 'function' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches

  const connection = (navigator as Navigator & { connection?: NetworkInformation }).connection
  const isConstrainedNetwork = Boolean(
    connection?.saveData ||
    connection?.effectiveType === 'slow-2g' ||
    connection?.effectiveType === '2g'
  )

  shouldPlayVideo.value = !prefersReducedMotion && !isConstrainedNetwork
})
</script>

<template>
  <main
    class="relative flex min-h-[calc(100dvh-5rem)] w-full flex-col overflow-hidden bg-[#f7efed] lg:flex-row lg:items-center lg:bg-gradient-to-b lg:from-[#6baae0] lg:via-[#8cc0ea] lg:to-[#b2d5f1]"
  >
    <div class="relative aspect-video w-full shrink-0 overflow-hidden bg-[#8cc0ea] lg:absolute lg:inset-0 lg:h-full lg:aspect-auto">
    <!-- Instant lightweight poster for immediate first paint & slow networks -->
    <img
      src="/404-poster.webp"
      alt=""
      aria-hidden="true"
      fetchpriority="high"
      decoding="async"
      class="pointer-events-none absolute inset-0 h-full w-full object-cover object-center"
    />

    <!-- Streaming looping video (skipped on Save-Data, 2G, or reduced-motion) -->
    <video
      v-if="shouldPlayVideo"
      autoplay
      muted
      loop
      playsinline
      preload="metadata"
      poster="/404-poster.webp"
      aria-hidden="true"
      class="pointer-events-none absolute inset-0 h-full w-full object-cover object-center transition-opacity duration-500"
      :class="videoReady ? 'opacity-100' : 'opacity-0'"
      @canplay="videoReady = true"
    >
      <source src="/404.mp4" type="video/mp4" />
    </video>

    </div>

    <!-- Content positioned in the open left sky on desktop (never overlapping the center sign) -->
    <div class="relative z-10 mx-auto flex w-full max-w-[1920px] flex-1 items-center px-4 py-6 sm:px-8 sm:py-10 lg:block lg:flex-none lg:py-16 lg:pl-10 xl:pl-20 2xl:pl-24">
      <section
        aria-labelledby="not-found-title"
        class="mx-auto w-full max-w-md rounded-[24px] border border-white/75 bg-background/88 p-6 text-center shadow-[0_24px_60px_-24px_rgba(33,26,26,0.28)] backdrop-blur-md sm:p-8 lg:mx-0 lg:max-w-[340px] lg:text-left xl:max-w-[400px] 2xl:max-w-[440px]"
      >
        <span class="inline-flex items-center rounded-full bg-primary/55 px-3.5 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-gold">
          Error 404
        </span>

        <h1
          id="not-found-title"
          class="mt-3.5 font-heading text-2xl font-semibold leading-tight text-dark sm:text-3xl"
        >
          This page could not be found
        </h1>

        <p class="mt-3 text-sm leading-relaxed text-muted">
          The page you are looking for does not exist or may have been moved. Let’s guide you back to our collection.
        </p>

        <div class="mt-6 flex flex-col items-stretch justify-center gap-3 min-[400px]:flex-row lg:justify-start">
          <router-link
            to="/"
            class="inline-flex min-h-11 items-center justify-center rounded-full bg-dark px-6 text-sm font-semibold text-background transition-all hover:bg-dark/90 active:scale-[0.98] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold"
          >
            Return home
          </router-link>
          <router-link
            to="/catalog"
            class="inline-flex min-h-11 items-center justify-center rounded-full border border-primary bg-white/90 px-6 text-sm font-semibold text-dark transition-all hover:bg-primary/30 active:scale-[0.98] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold"
          >
            Browse the shop
          </router-link>
        </div>
      </section>
    </div>
  </main>
</template>
