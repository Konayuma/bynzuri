<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import {
  Truck,
  RotateCcw,
  CreditCard,
  UserCircle,
  MessageCircle,
  Mail,
  MapPin,
  ChevronDown,
  HelpCircle,
  Search,
  Package,
  Send,
  CheckCircle2,
} from '@lucide/vue'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import BaseSelect from '@/components/base/BaseSelect.vue'
import type { SelectOption } from '@/components/base/BaseSelect.vue'
import { supportService, type SupportTopic } from '@/services/support.service'
import { useUserStore } from '@/stores/user'
import { isEmail } from '@/utils/formValidation'

const SUPPORT_EMAIL = 'hairskincare@bynzuri.com'

const userStore = useUserStore()
const openFaq = ref<string | null>(null)
const whatsappNumber = (import.meta.env.VITE_WHATSAPP_NUMBER || '').replace(/[^\d]/g, '')

const topicOptions: SelectOption[] = [
  { value: 'order', label: 'Order & Delivery' },
  { value: 'payment', label: 'Payments & Refunds' },
  { value: 'product', label: 'Product Advice' },
  { value: 'account', label: 'Account & Password' },
  { value: 'returns', label: 'Returns & Exchanges' },
  { value: 'general', label: 'General Inquiry' },
]

const name = ref('')
const email = ref('')
const phone = ref('')
const topic = ref<SupportTopic>('general')
const orderReference = ref('')
const subject = ref('')
const message = ref('')
const website = ref('')

const submitting = ref(false)
const submitError = ref('')
const fieldErrors = ref<Record<string, string>>({})
const submittedReference = ref('')
const submittedEmail = ref('')

const showOrderHint = computed(() => ['order', 'payment', 'returns'].includes(topic.value))

watch(
  () => userStore.user,
  (user) => {
    if (!user) return
    if (!name.value) {
      name.value = [user.first_name, user.last_name].filter(Boolean).join(' ').trim()
    }
    if (!email.value && user.email) {
      email.value = user.email
    }
    if (!phone.value && user.phone) {
      phone.value = user.phone
    }
  },
  { immediate: true }
)

watch(name, () => { delete fieldErrors.value.name; submitError.value = '' })
watch(email, () => { delete fieldErrors.value.email; submitError.value = '' })
watch(subject, () => { delete fieldErrors.value.subject; submitError.value = '' })
watch(message, () => { delete fieldErrors.value.message; submitError.value = '' })

function toggleFaq(id: string) {
  openFaq.value = openFaq.value === id ? null : id
}

function validateForm(): boolean {
  const errors: Record<string, string> = {}
  const trimmedName = name.value.trim()
  const trimmedEmail = email.value.trim().toLowerCase()
  const trimmedSubject = subject.value.trim()
  const trimmedMessage = message.value.trim()

  if (trimmedName.length < 2) {
    errors.name = 'Enter your name (at least 2 characters).'
  }
  if (!trimmedEmail) {
    errors.email = 'Enter your email address.'
  } else if (!isEmail(trimmedEmail)) {
    errors.email = 'Enter a valid email address.'
  }
  if (trimmedSubject.length < 3) {
    errors.subject = 'Enter a short subject (at least 3 characters).'
  }
  if (trimmedMessage.length < 10) {
    errors.message = 'Please enter at least 10 characters describing how we can help.'
  }

  fieldErrors.value = errors
  if (Object.keys(errors).length > 0) {
    submitError.value = 'Please check the highlighted fields and try again.'
    return false
  }
  submitError.value = ''
  return true
}

async function handleSubmit() {
  if (!validateForm()) return

  submitting.value = true
  submitError.value = ''
  try {
    const trimmedEmail = email.value.trim().toLowerCase()
    const result = await supportService.submitInquiry({
      name: name.value.trim(),
      email: trimmedEmail,
      phone: phone.value.trim() || undefined,
      topic: topic.value,
      order_reference: orderReference.value.trim() || undefined,
      subject: subject.value.trim(),
      message: message.value.trim(),
      website: website.value,
    })
    submittedReference.value = result.reference
    submittedEmail.value = trimmedEmail
    orderReference.value = ''
    subject.value = ''
    message.value = ''
  } catch (err: unknown) {
    const response = (err as { response?: { status?: number; data?: Record<string, unknown> } })?.response
    if (response?.status === 429) {
      submitError.value = 'You have sent several inquiries recently. Please wait a little while before sending another.'
    } else if (response?.data && typeof response.data === 'object') {
      const nextErrors: Record<string, string> = {}
      for (const [key, val] of Object.entries(response.data)) {
        if (key === 'detail' && typeof val === 'string') {
          submitError.value = val
        } else if (Array.isArray(val) && typeof val[0] === 'string') {
          nextErrors[key] = val[0]
        }
      }
      fieldErrors.value = nextErrors
      if (!submitError.value) {
        submitError.value = Object.keys(nextErrors).length
          ? 'Please check the highlighted fields and try again.'
          : 'We could not send your inquiry right now. Please try again or email us directly.'
      }
    } else {
      submitError.value = 'We could not send your inquiry right now. Please try again or email us directly.'
    }
  } finally {
    submitting.value = false
  }
}

function resetInquiry() {
  submittedReference.value = ''
  submittedEmail.value = ''
  submitError.value = ''
  fieldErrors.value = {}
}

const faqs = [
  {
    id: 'delivery',
    icon: Truck,
    question: 'How long does delivery take?',
    answer: 'We deliver across Zambia in 1–5 business days. Lusaka orders usually arrive within 1–2 days — other provinces take 3–5 days. We\'ll send you email updates as your order is confirmed and dispatched.',
  },
  {
    id: 'returns',
    icon: RotateCcw,
    question: 'What is your return policy?',
    answer: `We accept returns within 7 days of delivery. Items must be unused, unopened, and in their original packaging. To start a return, send us an inquiry using the form above with your order number, or email ${SUPPORT_EMAIL}.`,
  },
  {
    id: 'payments',
    icon: CreditCard,
    question: 'What payment methods do you accept?',
    answer: 'We accept MTN Mobile Money and Airtel Money. After placing your order, you\'ll receive a payment request via mobile money (SMS or USSD prompt), and we\'ll email your receipt once payment is confirmed.',
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
    answer: 'We send email updates when your order is placed, paid, dispatched, and delivered. You can also check your order status anytime from your account\'s Order History page.',
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
        <p class="text-xs font-semibold uppercase tracking-[0.18em] text-gold mb-2">Help &amp; Support</p>
        <h1 class="font-heading text-3xl md:text-4xl font-semibold text-dark mb-3">How can we help?</h1>
        <p class="text-muted text-sm md:text-base max-w-lg mx-auto mb-6">
          Find quick answers below or send our team a direct inquiry — we typically reply within 24 hours.
        </p>
        <a
          href="#contact-form"
          class="inline-flex items-center gap-2 rounded-full bg-dark px-5 py-2.5 text-sm font-medium text-white hover:bg-dark/90 transition-colors"
        >
          <Send class="w-4 h-4" aria-hidden="true" />
          Send an Inquiry
        </a>
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
              <Search class="w-5 h-5 text-dark" aria-hidden="true" />
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
              <Package class="w-5 h-5 text-dark" aria-hidden="true" />
            </div>
            <div>
              <p class="text-sm font-medium text-dark">Order History</p>
              <p class="text-xs text-muted">View past orders and status</p>
            </div>
          </router-link>

          <router-link
            to="/auth/forgot-password"
            class="flex items-center gap-3 bg-white rounded-[20px] p-5 shadow-[0_8px_30px_rgba(0,0,0,0.06)] hover:shadow-[0_8px_30px_rgba(0,0,0,0.1)] transition-shadow"
          >
            <div class="w-10 h-10 rounded-full bg-nzuri-blush/50 flex items-center justify-center shrink-0">
              <UserCircle class="w-5 h-5 text-dark" aria-hidden="true" />
            </div>
            <div>
              <p class="text-sm font-medium text-dark">Reset Password</p>
              <p class="text-xs text-muted">Request a new reset link</p>
            </div>
          </router-link>
        </div>
      </section>

      <!-- Support Inquiry Form -->
      <section id="contact-form" class="scroll-mt-24">
        <div class="bg-white rounded-[24px] p-6 sm:p-8 shadow-[0_8px_30px_rgba(0,0,0,0.06)] border border-primary/20">
          <div class="mb-6">
            <h2 class="font-heading text-xl font-semibold text-dark">Send an Inquiry</h2>
            <p class="text-sm text-muted mt-1">
              Have a question about an order, product recommendation, payment, or account? Send us a message and our team will reply to your email.
            </p>
          </div>

          <div
            v-if="submittedReference"
            role="status"
            aria-live="polite"
            class="rounded-[18px] bg-nzuri-blush/35 border border-primary/40 p-6 text-center space-y-3"
          >
            <div class="w-12 h-12 rounded-full bg-white mx-auto flex items-center justify-center shadow-sm">
              <CheckCircle2 class="w-6 h-6 text-green-700" aria-hidden="true" />
            </div>
            <h3 class="font-heading text-lg font-semibold text-dark">Inquiry Sent</h3>
            <p class="text-sm text-muted max-w-md mx-auto">
              Thank you for reaching out. Your inquiry has been received with reference
              <strong class="text-dark">{{ submittedReference }}</strong>.
              Our team will reply to <strong class="text-dark">{{ submittedEmail }}</strong> within 24 hours.
            </p>
            <div class="pt-2">
              <BaseButton variant="secondary" @click="resetInquiry">
                Send Another Inquiry
              </BaseButton>
            </div>
          </div>

          <form v-else novalidate @submit.prevent="handleSubmit" class="space-y-4">
            <!-- Honeypot field for basic spam protection -->
            <div class="hidden" aria-hidden="true">
              <label for="support-website">Website</label>
              <input id="support-website" v-model="website" type="text" tabindex="-1" autocomplete="off" />
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <BaseInput
                id="support-name"
                v-model="name"
                label="Your Name"
                type="text"
                required
                autocomplete="name"
                placeholder="Full name"
                :error="fieldErrors.name"
              />
              <BaseInput
                id="support-email"
                v-model="email"
                label="Email Address"
                type="email"
                required
                autocomplete="email"
                placeholder="you@example.com"
                :error="fieldErrors.email"
              />
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <BaseSelect
                id="support-topic"
                v-model="topic"
                label="Topic"
                required
                :options="topicOptions"
                :error="fieldErrors.topic"
              />
              <BaseInput
                id="support-phone"
                v-model="phone"
                label="Phone / WhatsApp (Optional)"
                type="tel"
                autocomplete="tel"
                placeholder="+260 97 ..."
                :error="fieldErrors.phone"
              />
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <BaseInput
                id="support-subject"
                v-model="subject"
                label="Subject"
                type="text"
                required
                placeholder="Brief summary of your question"
                :error="fieldErrors.subject"
              />
              <BaseInput
                id="support-order-ref"
                v-model="orderReference"
                :label="showOrderHint ? 'Order Number (Recommended)' : 'Order Number (Optional)'"
                type="text"
                placeholder="e.g. 8-character order ID"
                :error="fieldErrors.order_reference"
              />
            </div>

            <div class="space-y-1.5">
              <div class="flex items-center justify-between">
                <label for="support-message" class="block text-sm font-semibold text-dark">
                  Message <span class="text-gold" aria-hidden="true">*</span>
                </label>
                <span class="text-xs text-muted tabular-nums">{{ message.length }} / 3000</span>
              </div>
              <textarea
                id="support-message"
                v-model="message"
                rows="5"
                maxlength="3000"
                required
                placeholder="Tell us how we can help..."
                :aria-invalid="fieldErrors.message ? 'true' : undefined"
                :aria-describedby="fieldErrors.message ? 'support-message-error' : undefined"
                class="w-full px-4 py-3 text-base sm:text-sm bg-white border rounded-[14px] text-dark placeholder:text-muted/70 shadow-sm transition-[border-color,box-shadow] focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/25 resize-y"
                :class="fieldErrors.message ? 'border-red-600' : 'border-[#b9a8a8] hover:border-gold/70'"
              />
              <p v-if="fieldErrors.message" id="support-message-error" role="alert" class="text-sm text-red-700">
                {{ fieldErrors.message }}
              </p>
            </div>

            <p v-if="submitError" role="alert" class="text-sm text-red-700">
              {{ submitError }}
            </p>

            <div class="pt-1 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <p class="text-xs text-muted">
                Sent directly to <strong class="text-dark">{{ SUPPORT_EMAIL }}</strong>.
              </p>
              <BaseButton type="submit" variant="secondary" :loading="submitting">
                Send Inquiry
              </BaseButton>
            </div>
          </form>
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
              type="button"
              class="w-full flex items-center gap-3 p-5 text-left transition-colors hover:bg-primary/5 focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-gold"
              :aria-expanded="openFaq === faq.id"
              :aria-controls="`faq-panel-${faq.id}`"
              @click="toggleFaq(faq.id)"
            >
              <div class="w-9 h-9 rounded-full bg-nzuri-blush/50 flex items-center justify-center shrink-0">
                <component :is="faq.icon" class="w-4 h-4 text-dark" aria-hidden="true" />
              </div>
              <span class="flex-1 text-sm font-medium text-dark">{{ faq.question }}</span>
              <ChevronDown
                class="w-4 h-4 text-muted transition-transform duration-200 shrink-0"
                :class="openFaq === faq.id ? 'rotate-180' : ''"
                aria-hidden="true"
              />
            </button>
            <div
              v-show="openFaq === faq.id"
              :id="`faq-panel-${faq.id}`"
            >
              <p class="px-5 pb-5 sm:pl-[76px] text-sm text-muted leading-relaxed">
                {{ faq.answer }}
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Direct Contact -->
      <section>
        <h2 class="font-heading text-lg font-semibold text-dark mb-4">Other Ways to Reach Us</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <a
            :href="`mailto:${SUPPORT_EMAIL}`"
            class="flex items-center gap-3 bg-white rounded-[20px] p-5 shadow-[0_8px_30px_rgba(0,0,0,0.06)] hover:shadow-[0_8px_30px_rgba(0,0,0,0.1)] transition-shadow"
          >
            <div class="w-10 h-10 rounded-full bg-nzuri-blush/50 flex items-center justify-center shrink-0">
              <Mail class="w-5 h-5 text-dark" aria-hidden="true" />
            </div>
            <div class="min-w-0">
              <p class="text-sm font-medium text-dark">Email Us Directly</p>
              <p class="text-xs text-muted truncate">{{ SUPPORT_EMAIL }}</p>
            </div>
          </a>

          <a
            v-if="whatsappNumber"
            :href="`https://wa.me/${whatsappNumber}`"
            target="_blank"
            rel="noopener noreferrer"
            class="flex items-center gap-3 bg-white rounded-[20px] p-5 shadow-[0_8px_30px_rgba(0,0,0,0.06)] hover:shadow-[0_8px_30px_rgba(0,0,0,0.1)] transition-shadow"
          >
            <div class="w-10 h-10 rounded-full bg-green-50 flex items-center justify-center shrink-0">
              <MessageCircle class="w-5 h-5 text-green-600" aria-hidden="true" />
            </div>
            <div>
              <p class="text-sm font-medium text-dark">WhatsApp</p>
              <p class="text-xs text-muted">We reply within a few hours</p>
            </div>
          </a>

          <div
            v-else
            class="flex items-center gap-3 bg-white rounded-[20px] p-5 shadow-[0_8px_30px_rgba(0,0,0,0.06)]"
          >
            <div class="w-10 h-10 rounded-full bg-nzuri-blush/50 flex items-center justify-center shrink-0">
              <MapPin class="w-5 h-5 text-dark" aria-hidden="true" />
            </div>
            <div>
              <p class="text-sm font-medium text-dark">Location</p>
              <p class="text-xs text-muted">Lusaka, Zambia</p>
            </div>
          </div>
        </div>

        <div v-if="whatsappNumber" class="mt-4 bg-white rounded-[20px] p-5 shadow-[0_8px_30px_rgba(0,0,0,0.06)]">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-nzuri-blush/50 flex items-center justify-center shrink-0">
              <MapPin class="w-5 h-5 text-dark" aria-hidden="true" />
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
