<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Check, Mail, ShieldCheck } from '@lucide/vue'
import { authService } from '@/services/auth.service'
import { getVerificationEmail, rememberVerificationEmail } from '@/services/verification-context'
import { isEmail } from '@/utils/formValidation'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'

const route = useRoute()
const router = useRouter()
// Accept existing links while removing their address from the visible URL.
const legacyEmail = typeof route.query.email === 'string' ? route.query.email : ''
if (legacyEmail) rememberVerificationEmail(legacyEmail)
const email = ref(legacyEmail || getVerificationEmail())
const needsEmail = ref(!email.value)
const code = ref('')
const loading = ref(false)
const resending = ref(false)
const error = ref('')
const notice = ref('')
const success = ref(false)

onMounted(() => {
  if (legacyEmail) {
    const query = { ...route.query }
    delete query.email
    void router.replace({ path: route.path, query, hash: route.hash })
  }
})

async function verify() {
  if (loading.value || resending.value) return
  error.value = ''
  notice.value = ''
  if (!isEmail(email.value)) { needsEmail.value = true; error.value = 'Enter the valid email address you used to create your account.'; return }
  if (!/^\d{6}$/.test(code.value.trim())) { error.value = 'Enter the six-digit code from your email.'; return }
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
  } finally { loading.value = false }
}

async function resend() {
  if (resending.value || loading.value) return
  if (!isEmail(email.value)) { needsEmail.value = true; error.value = 'Enter the valid email address you used to create your account.'; return }
  error.value = ''
  notice.value = ''
  resending.value = true
  try {
    rememberVerificationEmail(email.value)
    await authService.resendVerificationEmail(email.value.trim())
    notice.value = 'If your account still needs verification, a new code will be sent. Allow a few minutes and check your spam folder. You can request a code once per minute.'
  } catch (cause: unknown) {
    const response = cause as { response?: { status?: number } }
    error.value = response.response?.status === 429 ? 'Too many requests. Please wait before trying again.' : 'We could not request a code. Check your connection and try again.'
  } finally { resending.value = false }
}

function signIn(verified: boolean) {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
  router.push({ path: '/auth/login', query: { ...(verified ? { verified: '1' } : {}), ...(redirect.startsWith('/') && !redirect.startsWith('//') ? { redirect } : {}) } })
}
</script>

<template>
  <div class="flex min-h-[min(80vh,720px)] items-center justify-center px-4 py-12 sm:py-16">
    <section class="w-full max-w-md" aria-labelledby="verification-title">
      <template v-if="success">
        <div class="mb-6 flex h-14 w-14 items-center justify-center rounded-full bg-primary/35 text-dark"><Check class="h-6 w-6" aria-hidden="true" /></div>
        <p class="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-gold">Account ready</p>
        <h1 id="verification-title" class="font-heading text-2xl font-semibold text-dark sm:text-3xl">Email verified</h1>
        <p class="mt-3 text-base leading-relaxed text-muted">Your account is ready. Sign in to continue.</p>
        <BaseButton variant="secondary" fullWidth class="mt-7 min-h-12" @click="signIn(true)">Continue to sign in</BaseButton>
      </template>
      <template v-else>
        <div class="mb-6 flex h-14 w-14 items-center justify-center rounded-full bg-primary/35 text-dark"><Mail class="h-6 w-6" aria-hidden="true" /></div>
        <p class="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-gold">One last step</p>
        <h1 id="verification-title" class="font-heading text-2xl font-semibold text-dark sm:text-3xl">Check your inbox</h1>
        <p class="mt-3 text-base leading-relaxed text-muted">Enter the six-digit code sent to your email to finish setting up your account.</p>
        <form class="mt-7 space-y-5" novalidate @submit.prevent="verify">
          <BaseInput v-if="needsEmail" id="verification-email" v-model="email" label="Account email address" type="email" autocomplete="email" hint="Use the email address you signed up with." required />
          <BaseInput id="verification-code" v-model="code" label="Verification code" inputmode="numeric" pattern="[0-9]{6}" autocomplete="one-time-code" maxlength="6" placeholder="Enter six-digit code" hint="Your code expires 30 minutes after you request it." required />
          <p v-if="error" role="alert" class="rounded-xl bg-red-50 px-4 py-3 text-sm leading-relaxed text-red-800">{{ error }}</p>
          <p v-if="notice" role="status" class="rounded-xl bg-primary/20 px-4 py-3 text-sm leading-relaxed text-dark">{{ notice }}</p>
          <BaseButton type="submit" variant="secondary" fullWidth class="min-h-12" :loading="loading" :disabled="resending">Verify email</BaseButton>
        </form>
        <div class="mt-7 border-t border-primary/40 pt-5">
          <p class="text-sm leading-relaxed text-muted">Still waiting? Delivery can take a few minutes. Check your spam folder too.</p>
          <button type="button" class="mt-2 min-h-11 text-sm font-semibold text-dark underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold disabled:opacity-50" :disabled="resending || loading" @click="resend">{{ resending ? 'Requesting a code…' : 'Send a new code' }}</button>
          <button v-if="!needsEmail" type="button" class="ml-5 min-h-11 text-sm text-muted underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold" :disabled="resending || loading" @click="needsEmail = true; error = ''; notice = ''">Use another account</button>
        </div>
        <p class="mt-4 flex items-start gap-2 text-sm text-muted"><ShieldCheck class="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" /> Never share your code with anyone.</p>
        <p class="mt-4 text-sm text-muted">Already verified? <button type="button" class="min-h-11 font-medium text-dark underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-gold" @click="signIn(false)">Continue to sign in</button></p>
      </template>
    </section>
  </div>
</template>
