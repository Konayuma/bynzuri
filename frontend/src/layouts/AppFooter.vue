<script setup lang="ts">
</script>

<template>
  <footer class="bg-dark text-background mt-16">
    <div class="max-w-7xl mx-auto px-4 py-12">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div>
          <h3 class="font-heading text-xl font-semibold mb-4">bynzuri</h3>
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
            <li><a href="#" class="text-sm text-muted hover:text-background transition-colors">Delivery Information</a></li>
            <li><a href="#" class="text-sm text-muted hover:text-background transition-colors">Returns Policy</a></li>
            <li><a href="#" class="text-sm text-muted hover:text-background transition-colors">Contact Us</a></li>
            <li><a href="#" class="text-sm text-muted hover:text-background transition-colors">FAQ</a></li>
          </ul>
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
