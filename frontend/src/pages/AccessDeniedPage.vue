<template>
  <section class="mx-auto max-w-xl px-6 py-20 text-center">
    <h1 class="font-heading text-2xl font-semibold">Administrator access required</h1>
    <p class="mt-4 text-gray-600">Your account does not have permission to access this area. Sign in with a staff account or contact the site administrator.</p>
    <div class="mt-6 flex flex-wrap justify-center gap-4">
      <router-link class="underline" to="/">Return to the store</router-link>
      <router-link class="underline" :to="{ name: 'login', query: { redirect: '/admin' } }">Sign in with another account</router-link>
    </div>
  </section>
</template>
