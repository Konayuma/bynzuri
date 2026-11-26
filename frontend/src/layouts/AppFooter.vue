<template>
  <footer class="bg-dark text-background">
    <div class="max-w-7xl mx-auto px-4 py-12">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <div>
          <router-link to="/" aria-label="By Nzuri home" class="block w-44 h-28 -ml-6 -mt-5 mb-2"><img src="/By%20Nzuri%20Vector%20Logo%20-01.svg" alt="By Nzuri" class="w-full h-full object-contain brightness-0 invert" /></router-link>
          <p class="text-muted text-sm leading-relaxed">
            Premium beauty and haircare, delivered across Zambia.
            Healthy hair. Beautiful confidence.
          </p>
        </div>

        <div>
          <h4 class="font-body text-sm font-semibold uppercase tracking-wider mb-4">Shop</h4>
          <ul class="space-y-2">
            <li><router-link to="/catalog" class="text-sm text-muted hover:text-background transition-colors">All Products</router-link></li>
            <li><router-link to="/catalog?category=hair-care" class="text-sm text-muted hover:text-background transition-colors">Hair Care</router-link></li>
            <li><router-link to="/catalog?category=hair-growth" class="text-sm text-muted hover:text-background transition-colors">Hair Growth</router-link></li>
            <li><router-link to="/catalog?category=oils" class="text-sm text-muted hover:text-background transition-colors">Oils</router-link></li>
          </ul>
        </div>

        <div>
          <h4 class="font-body text-sm font-semibold uppercase tracking-wider mb-4">Support</h4>
          <ul class="space-y-2">
            <li><router-link to="/help" class="text-sm text-muted hover:text-background transition-colors">Help & Support</router-link></li>
            <li><span class="text-sm text-muted">Delivery: 1-5 business days</span></li>
            <li><span class="text-sm text-muted">Returns within 7 days</span></li>
            <li><a href="mailto:hairskincare@bynzuri.com" class="text-sm text-muted hover:text-background transition-colors">hairskincare@bynzuri.com</a></li>
            <li><span class="text-sm text-muted">Lusaka, Zambia</span></li>
          </ul>
        </div>

        <div>
          <h4 class="font-body text-sm font-semibold uppercase tracking-wider mb-4">Need help?</h4>
          <p class="text-sm text-muted mb-3">Questions about a product or an order?</p>
          <router-link to="/help#contact-form" class="text-sm underline text-background">Send an inquiry</router-link>
        </div>
      </div>

      <div class="border-t border-white/10 mt-8 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
        <p class="text-xs text-muted">
          &copy; {{ new Date().getFullYear() }} By Nzuri. All rights reserved.
        </p>
        <div class="flex gap-4 text-xs text-muted">
          <span class="flex items-center gap-1">
            <span class="w-1.5 h-1.5 rounded-full bg-success inline-block"></span>
            Secure Payments
          </span>
          <span class="flex items-center gap-1">
            <span class="w-1.5 h-1.5 rounded-full bg-gold inline-block"></span>
            Nationwide Delivery
          </span>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
footer :deep(.text-muted) { color: #c8b8b7; }
</style>
