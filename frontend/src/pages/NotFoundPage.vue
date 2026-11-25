<template>
  <main class="mx-auto flex max-w-2xl flex-col items-center px-4 py-12 text-center sm:px-6 sm:py-16">
    <div class="w-full max-w-lg overflow-hidden rounded-[24px] border border-primary/60 bg-primary/15 shadow-[0_20px_50px_-24px_rgba(33,26,26,0.22)]">
      <img
        src="/404.gif"
        alt="Blush pink floral road sign indicating page not found"
        class="aspect-video w-full object-cover"
      />
    </div>

    <span class="mt-7 inline-flex items-center rounded-full bg-primary/45 px-3.5 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-gold">
      Error 404
    </span>

    <h1 class="mt-3 font-heading text-2xl font-semibold text-dark sm:text-3xl">
      This page could not be found
    </h1>

    <p class="mt-3 max-w-md text-sm leading-relaxed text-muted">
      The page you are looking for does not exist or may have been moved. Let’s guide you back to our collection.
    </p>

    <div class="mt-7 flex flex-wrap items-center justify-center gap-3">
      <router-link
        to="/"
        class="inline-flex min-h-11 items-center justify-center rounded-full bg-dark px-6 text-sm font-semibold text-background transition-all hover:bg-dark/90 active:scale-[0.98] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold"
      >
        Return home
      </router-link>
      <router-link
        to="/catalog"
        class="inline-flex min-h-11 items-center justify-center rounded-full border border-primary bg-white px-6 text-sm font-semibold text-dark transition-all hover:bg-primary/25 active:scale-[0.98] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold"
      >
        Browse the shop
      </router-link>
    </div>
  </main>
</template>
