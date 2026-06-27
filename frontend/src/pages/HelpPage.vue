<script setup lang="ts">
import { ref } from 'vue'
import { Truck, RotateCcw, CreditCard, UserCircle, MessageCircle, Mail, MapPin, ChevronDown, HelpCircle, Search, Package } from '@lucide/vue'

const openFaq = ref<string | null>(null)

function toggleFaq(id: string) {
  openFaq.value = openFaq.value === id ? null : id
}

const faqs = [
  {
    id: 'delivery',
    icon: Truck,
    question: 'How long does delivery take?',
    answer: 'We deliver across Zambia in 1–5 business days. Lusaka orders usually arrive within 1–2 days — other provinces take 3–5 days. We\'ll send you tracking updates via WhatsApp once your order ships.',
  },
  {
    id: 'returns',
    icon: RotateCcw,
    question: 'What is your return policy?',
    answer: 'We accept returns within 7 days of delivery. Items must be unused, unopened, and in their original packaging. To start a return, message us on WhatsApp or email your order number and reason.',
  },
  {
    id: 'payments',
    icon: CreditCard,
    question: 'What payment methods do you accept?',
    answer: 'We accept MTN Mobile Money, Airtel Money, and Zamtel Kwacha. After placing your order, you\'ll receive a payment request via mobile money (SMS or USSD prompt).',
  },
  {
    id: 'account',
    icon: UserCircle,
    question: 'Do I need an account to order?',
    answer: 'You can browse products without signing up, but you\'ll need an account to place an order. Just provide your name, email, and a password — your order history and addresses will be saved for next time.',
  },
  {
    id: 'track-order',
    icon: Package,
    question: 'How do I track my order?',
    answer: 'Once your order ships, we\'ll send you a WhatsApp notification with delivery updates. You can also check your order status anytime from your account\'s Order History page.',
  },
  {
    id: 'products',
    icon: HelpCircle,
    question: 'Are your products safe for all hair types?',
    answer: 'Yes — all By Nzuri products are sulfate-free, silicone-free, and paraben-free. They\'re safe for natural hair, relaxed hair, locs, and children above 1 year. Our ingredients are 100% natural.',
  },
]
</script>

<template>
  <div class="min-h-[80vh]">
    <!-- Hero -->
    <section class="bg-nzuri-blush/40 py-12 px-4">
      <div class="max-w-3xl mx-auto text-center">
        <h1 class="font-heading text-3xl md:text-4xl font-semibold text-dark mb-3">How can we help?</h1>
        <p class="text-muted text-sm md:text-base max-w-lg mx-auto">
          Find answers or reach out to us directly.
        </p>
      </div>
    </section>

    <div class="max-w-3xl mx-auto px-4 py-10 space-y-10">
      <!-- Quick Links -->
      <section>
        <h2 class="font-heading text-lg font-semibold text-dark mb-4">Common Tasks</h2>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <router-link
            to="/catalog"
            class="flex items-center gap-3 bg-white rounded-[20px] p-5 shadow-[0_8px_30px_rgba(0,0,0,0.06)] hover:shadow-[0_8px_30px_rgba(0,0,0,0.1)] transition-shadow"
          >
            <div class="w-10 h-10 rounded-full bg-nzuri-blush/50 flex items-center justify-center shrink-0">
              <Search class="w-5 h-5 text-dark" />
            </div>
            <div>
              <p class="text-sm font-medium text-dark">Shop All Products</p>
              <p class="text-xs text-muted">Browse our full catalog</p>
            </div>
          </router-link>

          <router-link
            to="/account/orders"
            class="flex items-center gap-3 bg-white rounded-[20px] p-5 shadow-[0_8px_30px_rgba(0,0,0,0.06)] hover:shadow-[0_8px_30px_rgba(0,0,0,0.1)] transition-shadow"
          >
            <div class="w-10 h-10 rounded-full bg-nzuri-blush/50 flex items-center justify-center shrink-0">
              <Package class="w-5 h-5 text-dark" />
            </div>
            <div>
              <p class="text-sm font-medium text-dark">Order History</p>
              <p class="text-xs text-muted">View past orders and delivery status</p>
            </div>
          </router-link>

          <router-link
            to="/auth/forgot-password"
            class="flex items-center gap-3 bg-white rounded-[20px] p-5 shadow-[0_8px_30px_rgba(0,0,0,0.06)] hover:shadow-[0_8px_30px_rgba(0,0,0,0.1)] transition-shadow"
          >
            <div class="w-10 h-10 rounded-full bg-nzuri-blush/50 flex items-center justify-center shrink-0">
              <UserCircle class="w-5 h-5 text-dark" />
            </div>
            <div>
              <p class="text-sm font-medium text-dark">Forgot Password</p>
              <p class="text-xs text-muted">Reset your password</p>
            </div>
          </router-link>
        </div>
      </section>

      <!-- FAQ -->
      <section>
        <h2 class="font-heading text-lg font-semibold text-dark mb-4">Common Questions</h2>
        <div class="space-y-3">
          <div
            v-for="faq in faqs"
            :key="faq.id"
            class="bg-white rounded-[20px] shadow-[0_8px_30px_rgba(0,0,0,0.06)] overflow-hidden"
          >
            <button
              class="w-full flex items-center gap-3 p-5 text-left transition-colors hover:bg-primary/5"
              @click="toggleFaq(faq.id)"
            >
              <div class="w-9 h-9 rounded-full bg-nzuri-blush/50 flex items-center justify-center shrink-0">
                <component :is="faq.icon" class="w-4 h-4 text-dark" />
              </div>
              <span class="flex-1 text-sm font-medium text-dark">{{ faq.question }}</span>
              <ChevronDown
                class="w-4 h-4 text-muted transition-transform duration-200 shrink-0"
                :class="openFaq === faq.id ? 'rotate-180' : ''"
              />
            </button>
            <div
              class="overflow-hidden transition-all duration-300"
              :class="openFaq === faq.id ? 'max-h-60' : 'max-h-0'"
            >
              <p class="px-5 pb-5 pl-[76px] text-sm text-muted leading-relaxed">
                {{ faq.answer }}
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Contact -->
      <section>
        <h2 class="font-heading text-lg font-semibold text-dark mb-4">Get in Touch</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <a
            href="https://wa.me/260770000000"
            target="_blank"
            rel="noopener noreferrer"
            class="flex items-center gap-3 bg-white rounded-[20px] p-5 shadow-[0_8px_30px_rgba(0,0,0,0.06)] hover:shadow-[0_8px_30px_rgba(0,0,0,0.1)] transition-shadow"
          >
            <div class="w-10 h-10 rounded-full bg-green-50 flex items-center justify-center shrink-0">
              <MessageCircle class="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p class="text-sm font-medium text-dark">WhatsApp</p>
              <p class="text-xs text-muted">We reply within a few hours</p>
            </div>
          </a>

          <a
            href="mailto:hello@bynzuri.zm"
            class="flex items-center gap-3 bg-white rounded-[20px] p-5 shadow-[0_8px_30px_rgba(0,0,0,0.06)] hover:shadow-[0_8px_30px_rgba(0,0,0,0.1)] transition-shadow"
          >
            <div class="w-10 h-10 rounded-full bg-nzuri-blush/50 flex items-center justify-center shrink-0">
              <Mail class="w-5 h-5 text-dark" />
            </div>
            <div>
              <p class="text-sm font-medium text-dark">Email</p>
              <p class="text-xs text-muted">We respond within 24 hours</p>
            </div>
          </a>
        </div>

        <div class="mt-4 bg-white rounded-[20px] p-5 shadow-[0_8px_30px_rgba(0,0,0,0.06)]">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-nzuri-blush/50 flex items-center justify-center shrink-0">
              <MapPin class="w-5 h-5 text-dark" />
            </div>
            <div>
              <p class="text-sm font-medium text-dark">Location</p>
              <p class="text-xs text-muted">Lusaka, Zambia</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
