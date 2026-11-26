<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Check, Mail, ShieldCheck } from '@lucide/vue'
import { authService } from '@/services/auth.service'
import { clearSignupCredentials, getVerificationEmail, rememberVerificationEmail, takeSignupCredentials } from '@/services/verification-context'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'
import { isEmail } from '@/utils/formValidation'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const cartStore = useCartStore()

// Resolve email from previous page (router state or session storage) or legacy link.
const stateEmail = typeof window !== 'undefined' && typeof window.history.state?.email === 'string'
  ? window.history.state.email.trim()
  : ''
const legacyEmail = typeof route.query.email === 'string' ? route.query.email.trim() : ''
const initialEmail = stateEmail || legacyEmail || getVerificationEmail()
if (initialEmail) rememberVerificationEmail(initialEmail)

const email = ref(initialEmail)
const needsEmail = ref(!email.value)
const code = ref('')
const loading = ref(false)
const resending = ref(false)
const error = ref('')
const notice = ref('')
const success = ref(false)
const signingIn = ref(false)

function onCodeInput(event: Event) {
  const input = event.target as HTMLInputElement
  const digits = input.value.replace(/\D/g, '').slice(0, 6)
  code.value = digits
  if (input.value !== digits) input.value = digits
  error.value = ''
}

onMounted(async () => {
  if (legacyEmail) {
    const query = { ...route.query }
    delete query.email
    void router.replace({ path: route.path, query, hash: route.hash })
  }
  await nextTick()
  if (!needsEmail.value) {
    document.getElementById('verification-code')?.focus()
  }
})
onUnmounted(clearSignupCredentials)

async function verify() {
  if (loading.value || resending.value) return
  error.value = ''
  notice.value = ''
  if (!isEmail(email.value)) {
    needsEmail.value = true
    error.value = 'Enter the valid email address you used to create your account.'
    return
  }
  if (!/^\d{6}$/.test(code.value.trim())) {
    error.value = 'Enter the six-digit code from your email.'
    return
  }
  rememberVerificationEmail(email.value)
  loading.value = true
  try {
    await authService.verifyEmail(email.value.trim(), code.value.trim())
    rememberVerificationEmail('')
    success.value = true
  } catch (cause: unknown) {
    const response = cause as { response?: { status?: number } }
    error.value = response.response?.status === 400
      ? 'That code is incorrect or has expired. Check the latest email or request a new code.'
      : response.response?.status === 429
        ? 'Too many attempts. Please wait before trying again.'
        : 'We could not verify your email. Check your connection and try again.'
    return
  } finally {
    loading.value = false
  }

  const credentials = takeSignupCredentials(email.value)
  if (!credentials) return
  signingIn.value = true
  try {
    try { await userStore.login(credentials.email, credentials.password) }
    finally { credentials.password = '' }
    try {
      await cartStore.mergeGuestCart()
      await cartStore.fetchCart()
    } catch {
      cartStore.error = 'Signed in, but your cart could not be restored. Please try again.'
    }
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
    await router.replace(redirect.startsWith('/') && !redirect.startsWith('//') ? redirect : '/')
  } catch {
    // Verification already succeeded; never ask the customer to reuse the code.
    success.value = true
  } finally {
    signingIn.value = false
  }
}

async function resend() {
  if (resending.value || loading.value) return
  if (!isEmail(email.value)) {
    needsEmail.value = true
    error.value = 'Enter the valid email address you used to create your account.'
    return
  }
  error.value = ''
  notice.value = ''
  resending.value = true
  try {
    rememberVerificationEmail(email.value)
    await authService.resendVerificationEmail(email.value.trim())
    notice.value = 'If your account still needs verification, a new code will be sent. Allow a few minutes and check your spam folder. You can request a code once per minute.'
  } catch (cause: unknown) {
    const response = cause as { response?: { status?: number } }
    error.value = response.response?.status === 429
      ? 'Too many requests. Please wait before trying again.'
      : 'We could not request a code. Check your connection and try again.'
  } finally {
    resending.value = false
  }
}

function signIn(verified: boolean) {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
  router.push({
    path: '/auth/login',
    query: {
      ...(verified ? { verified: '1' } : {}),
      ...(redirect.startsWith('/') && !redirect.startsWith('//') ? { redirect } : {}),
    }
  })
}
</script>

<template>
  <div class="flex min-h-[min(80vh,720px)] items-center justify-center px-4 py-12 sm:py-16">
    <section class="w-full max-w-md mx-auto" aria-labelledby="verification-title">
      <template v-if="success">
        <div class="text-center">
          <div class="mx-auto mb-6 flex h-14 w-14 items-center justify-center rounded-full bg-primary/35 text-dark">
            <Check class="h-6 w-6" aria-hidden="true" />
          </div>
          <p class="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-gold">Account ready</p>
          <h1 id="verification-title" class="font-heading text-2xl font-semibold text-dark sm:text-3xl">Email verified</h1>
          <p v-if="signingIn" role="status" class="mt-3 text-base leading-relaxed text-muted">Your email is verified. Signing you in…</p>
          <template v-else>
            <p class="mt-3 text-base leading-relaxed text-muted">Your email is verified. Sign in to continue.</p>
            <BaseButton variant="secondary" fullWidth class="mt-7 min-h-12" @click="signIn(true)">Continue to sign in</BaseButton>
          </template>
        </div>
      </template>

      <template v-else>
        <div class="text-center">
          <div class="mx-auto mb-6 flex h-14 w-14 items-center justify-center rounded-full bg-primary/35 text-dark">
            <Mail class="h-6 w-6" aria-hidden="true" />
          </div>
          <p class="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-gold">One last step</p>
          <h1 id="verification-title" class="font-heading text-2xl font-semibold text-dark sm:text-3xl">Check your inbox</h1>
          <p v-if="!needsEmail && email" class="mt-3 text-sm sm:text-base leading-relaxed text-muted">
            Enter the 6-digit code sent to <strong class="font-semibold text-dark break-all">{{ email }}</strong>.
          </p>
          <p v-else class="mt-3 text-sm sm:text-base leading-relaxed text-muted">
            Enter the 6-digit code sent to your email to finish setting up your account.
          </p>
        </div>

        <form class="mt-7 space-y-5" novalidate @submit.prevent="verify">
          <BaseInput
            v-if="needsEmail"
            id="verification-email"
            v-model="email"
            label="Account email address"
            type="email"
            autocomplete="email"
            hint="Use the email address you signed up with."
            required
          />

          <div>
            <label for="verification-code" class="block text-sm font-medium text-dark mb-1.5 text-center">
              Verification code <span class="text-gold">*</span>
            </label>
            <input
              id="verification-code"
              :value="code"
              type="text"
              inputmode="numeric"
              pattern="[0-9]{6}"
              autocomplete="one-time-code"
              maxlength="6"
              placeholder="000000"
              required
              aria-describedby="verification-code-hint"
              class="w-full h-14 px-4 bg-white border border-primary/60 rounded-[14px] text-center text-2xl font-semibold tracking-[0.45em] text-dark tabular-nums placeholder:text-muted/35 focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/25 transition-colors"
              @input="onCodeInput"
            />
            <p id="verification-code-hint" class="mt-1.5 text-xs text-muted text-center">
              Your code expires 30 minutes after you request it.
            </p>
          </div>

          <p v-if="error" role="alert" class="rounded-xl bg-red-50 px-4 py-3 text-sm leading-relaxed text-red-800">{{ error }}</p>
          <p v-if="notice" role="status" class="rounded-xl bg-primary/20 px-4 py-3 text-sm leading-relaxed text-dark">{{ notice }}</p>

          <BaseButton type="submit" variant="secondary" fullWidth class="min-h-12" :loading="loading" :disabled="resending">
            Verify email
          </BaseButton>
        </form>

        <div class="mt-7 border-t border-primary/40 pt-5 text-center">
          <p class="text-sm leading-relaxed text-muted">Still waiting? Delivery can take a few minutes. Check your spam folder too.</p>
          <div class="mt-2 flex flex-wrap items-center justify-center gap-x-5 gap-y-1">
            <button
              type="button"
              class="min-h-11 text-sm font-semibold text-dark underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold disabled:opacity-50"
              :disabled="resending || loading"
              @click="resend"
            >
              {{ resending ? 'Requesting a code…' : 'Send a new code' }}
            </button>
            <button
              v-if="!needsEmail"
              type="button"
              class="min-h-11 text-sm text-muted underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold"
              :disabled="resending || loading"
              @click="clearSignupCredentials(); needsEmail = true; error = ''; notice = ''"
            >
              Change email
            </button>
          </div>
        </div>

        <p class="mt-4 flex items-center justify-center gap-2 text-xs text-muted">
          <ShieldCheck class="h-4 w-4 shrink-0" aria-hidden="true" />
          Never share your code with anyone.
        </p>

        <p class="mt-4 text-center text-sm text-muted">
          Already verified?
          <button
            type="button"
            class="min-h-11 font-medium text-dark underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-gold"
            @click="signIn(false)"
          >
            Continue to sign in
          </button>
        </p>
      </template>
    </section>
  </div>
</template>
