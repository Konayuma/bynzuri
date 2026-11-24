<template>
  <main class="mx-auto max-w-xl px-6 py-24 text-center">
    <p class="mb-2 text-xs font-semibold uppercase tracking-[.16em] text-gold">404</p>
    <h1 class="font-heading text-3xl font-semibold text-dark">Page not found</h1>
    <p class="mt-4 text-sm leading-relaxed text-muted">
      The page you are looking for does not exist or may have been moved.
    </p>
    <div class="mt-8 flex flex-wrap justify-center gap-4">
      <router-link
        to="/"
        class="inline-flex min-h-11 items-center justify-center rounded-[14px] bg-dark px-5 text-sm font-semibold text-white transition-colors hover:bg-dark/90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold"
      >
        Return home
      </router-link>
      <router-link
        to="/catalog"
        class="inline-flex min-h-11 items-center justify-center rounded-[14px] border border-[#b9a8a8] bg-white px-5 text-sm font-semibold text-dark transition-colors hover:bg-primary/20 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold"
      >
        Browse the shop
      </router-link>
    </div>
  </main>
</template>
