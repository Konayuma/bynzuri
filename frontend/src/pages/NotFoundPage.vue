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
    class="relative flex min-h-[calc(100dvh-5rem)] w-full items-end overflow-hidden bg-gradient-to-b from-[#6baae0] via-[#8cc0ea] to-[#b2d5f1] lg:items-center"
  >
    <!-- Instant lightweight poster for immediate first paint & slow networks -->
    <img
      src="/404-poster.webp"
      alt=""
      aria-hidden="true"
      fetchpriority="high"
      decoding="async"
      class="pointer-events-none absolute inset-0 h-full w-full object-cover object-[50%_22%] lg:object-center"
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
      class="pointer-events-none absolute inset-0 h-full w-full object-cover object-[50%_22%] transition-opacity duration-500 lg:object-center"
      :class="videoReady ? 'opacity-100' : 'opacity-0'"
      @canplay="videoReady = true"
    >
      <source src="/404.mp4" type="video/mp4" />
    </video>

    <!-- Subtle bottom scrim on mobile only for crisp legibility -->
    <div
      aria-hidden="true"
      class="pointer-events-none absolute inset-x-0 bottom-0 h-56 bg-gradient-to-t from-dark/25 to-transparent lg:hidden"
    />

    <!-- Content positioned in the open left sky on desktop (never overlapping the center sign) -->
    <div class="relative z-10 mx-auto w-full max-w-[1920px] px-4 pb-6 pt-64 sm:px-8 sm:pb-10 sm:pt-72 lg:py-16 lg:pl-10 xl:pl-20 2xl:pl-24">
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

        <div class="mt-6 flex flex-wrap items-center justify-center gap-3 lg:justify-start">
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
