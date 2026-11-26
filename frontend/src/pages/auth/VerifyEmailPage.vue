<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authService } from '@/services/auth.service'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'

const route = useRoute()
const router = useRouter()
const email = ref(typeof route.query.email === 'string' ? route.query.email : '')
const code = ref('')
const loading = ref(false)
const resending = ref(false)
const error = ref('')
const notice = ref('')
const success = ref(false)

async function verify() {
  error.value = ''
  notice.value = ''
  if (!email.value.trim() || !/^\d{6}$/.test(code.value.trim())) {
    error.value = 'Enter your email address and the six-digit code.'
    return
  }
  loading.value = true
  try {
    await authService.verifyEmail(email.value.trim(), code.value.trim())
    success.value = true
  } catch (cause: unknown) {
    const response = cause as { response?: { status?: number } }
    error.value = response.response?.status === 400
      ? 'This code is incorrect or expired. Check it or request a new code.'
      : response.response?.status === 429
        ? 'Too many attempts. Please wait before trying again.'
        : 'We could not verify your email. Check your connection and try again.'
  } finally { loading.value = false }
}

async function resend() {
  if (!email.value.trim()) { error.value = 'Enter your email address first.'; return }
  error.value = ''
  notice.value = ''
  resending.value = true
  try {
    await authService.resendVerificationEmail(email.value.trim())
    notice.value = 'If your account is eligible, a new code will be sent. Please wait a minute between requests and check your spam folder.'
  } catch {
    error.value = 'We could not request a code. Please wait and try again.'
  } finally { resending.value = false }
}

function signIn() {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
  router.push({ path: '/auth/login', query: { verified: '1', ...(redirect.startsWith('/') && !redirect.startsWith('//') ? { redirect } : {}) } })
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center px-4 py-10">
    <div class="w-full max-w-sm">
      <template v-if="success">
        <h1 class="font-heading text-2xl font-semibold text-dark">Email verified</h1>
        <p class="mt-2 text-sm text-muted">Your account is ready. Sign in to continue.</p>
        <BaseButton variant="secondary" fullWidth class="mt-6" @click="signIn">Continue to sign in</BaseButton>
      </template>
      <template v-else>
        <h1 class="font-heading text-2xl font-semibold text-dark">Verify your email</h1>
        <p class="mt-2 text-sm leading-relaxed text-muted">Enter the six-digit code sent to your email. It can take a few minutes to arrive and expires 30 minutes after it is requested.</p>
        <form class="mt-6 space-y-4" @submit.prevent="verify">
          <BaseInput id="verification-email" v-model="email" label="Email address" type="email" autocomplete="email" required />
          <BaseInput id="verification-code" v-model="code" label="Verification code" inputmode="numeric" autocomplete="one-time-code" maxlength="6" required />
          <p v-if="error" role="alert" class="text-sm text-red-700">{{ error }}</p>
          <p v-if="notice" role="status" class="text-sm text-muted">{{ notice }}</p>
          <BaseButton type="submit" variant="secondary" fullWidth :loading="loading">Verify email</BaseButton>
        </form>
        <p class="mt-5 text-sm text-muted">Didn't receive a code? Check your spam folder.</p>
        <button type="button" class="mt-2 min-h-11 text-sm font-semibold text-dark underline disabled:opacity-50" :disabled="resending || loading" @click="resend">{{ resending ? 'Requesting…' : 'Send a new code' }}</button>
      </template>
    </div>
  </div>
</template>
