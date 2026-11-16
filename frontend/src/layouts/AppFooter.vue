<script setup lang="ts">
import { ref } from 'vue'

const email = ref('')
const subscribed = ref(false)

function handleSubscribe() {
  if (email.value.trim()) {
    localStorage.setItem('bynzuri_newsletter', email.value.trim())
    subscribed.value = true
    email.value = ''
  }
}
</script>

<template>
  <footer class="bg-dark text-background">
    <div class="max-w-7xl mx-auto px-4 py-12">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
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
            <li><router-link to="/help" class="text-sm text-muted hover:text-background transition-colors">Help & Support</router-link></li>
            <li><span class="text-sm text-muted">Delivery: 1-5 business days</span></li>
            <li><span class="text-sm text-muted">Returns within 7 days</span></li>
            <li><a href="mailto:hello@bynzuri.zm" class="text-sm text-muted hover:text-background transition-colors">hello@bynzuri.zm</a></li>
            <li><span class="text-sm text-muted">Lusaka, Zambia</span></li>
          </ul>
        </div>

        <div>
          <h4 class="font-body text-sm font-semibold uppercase tracking-wider mb-4">Stay Updated</h4>
          <p class="text-xs text-muted mb-3">Get notified about new products and deals.</p>
          <div v-if="!subscribed">
            <form @submit.prevent="handleSubscribe" class="flex gap-2">
              <input
                v-model="email"
                type="email"
                placeholder="Your email"
                required
                class="flex-1 px-3 py-2 bg-white/10 border border-white/10 rounded-lg text-sm text-background placeholder:text-muted/60 focus:outline-none focus:border-gold transition-colors"
              />
              <button
                type="submit"
                class="px-3 py-2 bg-gold text-dark text-sm font-medium rounded-lg hover:bg-gold/80 transition-colors"
              >
                Join
              </button>
            </form>
          </div>
          <p v-else class="text-sm text-success">You're in! Watch your inbox for updates.</p>
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
