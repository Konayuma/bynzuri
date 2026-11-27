<script setup lang="ts">
import { ref, watch } from 'vue'
import { authService } from '@/services/auth.service'
import { isEmail } from '@/utils/formValidation'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import axios from 'axios'

const stateEmail = typeof window !== 'undefined' && typeof window.history.state?.email === 'string'
  ? window.history.state.email.trim()
  : ''
const email = ref(stateEmail)
const loading = ref(false)
const error = ref('')
const emailError = ref('')
const sent = ref(false)

watch(email, () => { emailError.value = ''; error.value = '' })

async function handleForgotPassword() {
  const trimmed = email.value.trim().toLowerCase()
  if (!trimmed) {
    emailError.value = 'Enter your email address.'
    error.value = 'Enter your email address'
    return
  }
  if (!isEmail(trimmed)) {
    emailError.value = 'Enter a valid email address.'
    error.value = 'Enter a valid email address.'
    return
  }

  loading.value = true
  error.value = ''
  emailError.value = ''

  try {
    await authService.forgotPassword(trimmed, window.location.origin)
    sent.value = true
  } catch (cause) {
    error.value = axios.isAxiosError(cause) && cause.response?.status === 429
      ? 'Too many requests. Please wait a while and try again.'
      : 'We couldn’t request a reset link. Check your connection and try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center px-4">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <h1 class="font-heading text-2xl font-semibold text-dark">Reset Password</h1>
        <p v-if="!sent" class="text-sm text-muted mt-1">
          Enter your account email to request a link to set a By Nzuri password.
        </p>
        <p v-else class="text-sm text-muted mt-1">
          If an active account exists for that email, check your inbox and spam folder for a link. Delivery can take a few minutes.
        </p>
      </div>

      <form v-if="!sent" novalidate @submit.prevent="handleForgotPassword" class="space-y-4">
        <BaseInput
          v-model="email"
          label="Email"
          type="email"
          required
          id="forgot-email"
          autocomplete="email"
          :error="emailError"
        />

        <p v-if="error" role="alert" class="text-sm text-red-700">{{ error }}</p>

        <BaseButton type="submit" variant="secondary" fullWidth :loading="loading">
          Send Reset Link
        </BaseButton>
      </form>

      <div class="mt-6 rounded-xl border border-primary/50 bg-white p-4 text-sm text-muted">
        <p class="font-medium text-dark">Used Google to sign in?</p>
        <p class="mt-1">You can continue with Google on the sign-in page, or request a link above to set a separate By Nzuri password. This won’t change your Google password.</p>
        <p class="mt-2"><router-link to="/auth/login" class="font-medium text-dark underline">Go to sign in</router-link> · <a href="https://accounts.google.com/signin/recovery" target="_blank" rel="noopener noreferrer" class="font-medium text-dark underline">Recover your Google account</a></p>
      </div>

      <BaseButton v-if="sent" class="mt-4" variant="secondary" fullWidth @click="$router.push('/auth/login')">
        Back to Sign In
      </BaseButton>

      <p class="text-sm text-center text-muted mt-6">
        Remember your password?
        <router-link to="/auth/login" class="text-dark font-medium hover:underline">
          Sign in
        </router-link>
      </p>
      <p class="text-xs text-center text-muted mt-2">
        Need help?
        <router-link to="/help#contact-form" class="text-dark font-medium hover:underline">
          Contact Help &amp; Support
        </router-link>
      </p>
    </div>
  </div>
</template>
