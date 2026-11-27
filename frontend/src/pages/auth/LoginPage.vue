<script setup lang="ts">
import { ref, watch } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'
import { hasSession } from '@/services/api'
import { isEmail } from '@/utils/formValidation'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import GoogleSignInButton from '@/components/auth/GoogleSignInButton.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const cartStore = useCartStore()
const stateEmail = typeof window !== 'undefined' && typeof window.history.state?.email === 'string'
  ? window.history.state.email.trim()
  : ''
const email = ref(stateEmail)
const password = ref('')
const loading = ref(false)
const error = ref('')
const fieldErrors = ref<Record<string, string>>({})

function goToForgotPassword() {
  const trimmed = email.value.trim()
  void router.push({
    path: '/auth/forgot-password',
    state: trimmed ? { email: trimmed } : undefined,
  })
}

async function handleGoogleLogin(credential: string) {
  if (loading.value) return
  loading.value = true
  error.value = ''
  try {
    await userStore.loginWithGoogle(credential)
  } catch (cause) {
    error.value = axios.isAxiosError(cause) && typeof cause.response?.data?.detail === 'string'
      ? cause.response.data.detail
      : 'We could not sign you in with Google. Please try again.'
    loading.value = false
    return
  }
  try {
    await cartStore.mergeGuestCart()
    await cartStore.fetchCart()
  } catch {
    cartStore.error = 'Signed in, but your cart could not be restored. Please try again.'
  } finally {
    loading.value = false
  }
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
  await router.push(redirect.startsWith('/') && !redirect.startsWith('//') ? redirect : '/')
}

watch(email, () => { delete fieldErrors.value.email; error.value = '' })
watch(password, () => { delete fieldErrors.value.password; error.value = '' })

async function handleLogin() {
  const errors: Record<string, string> = {}
  const trimmedEmail = email.value.trim().toLowerCase()
  if (!trimmedEmail || !password.value) {
    if (!trimmedEmail) errors.email = 'Enter your email address.'
    if (!password.value) errors.password = 'Enter your password.'
    fieldErrors.value = errors
    error.value = 'Enter both your email and password to continue'
    return
  }
  if (!isEmail(trimmedEmail)) {
    fieldErrors.value = { email: 'Enter a valid email address.' }
    error.value = 'Enter a valid email address.'
    return
  }
  fieldErrors.value = {}

  loading.value = true
  error.value = ''

  try {
    await userStore.login(trimmedEmail, password.value)
  } catch (cause) {
    if (hasSession()) {
      error.value = 'Signed in, but we could not load your account. Check your connection and try again.'
    } else if (axios.isAxiosError(cause) && [400, 401].includes(cause.response?.status ?? 0)) {
      error.value = 'Email or password is incorrect. Please try again.'
    } else {
      error.value = 'We could not sign you in right now. Check your connection and try again.'
    }
    loading.value = false
    return
  }

  try {
    await cartStore.mergeGuestCart()
    await cartStore.fetchCart()
  } catch {
    // Signing in succeeds even when cart synchronization is temporarily unavailable.
    cartStore.error = 'Signed in, but your cart could not be restored. Please try again.'
  } finally {
    loading.value = false
  }
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
  await router.push(redirect.startsWith('/') && !redirect.startsWith('//') ? redirect : '/')
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center px-4">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <h1 class="font-heading text-2xl font-semibold text-dark">Welcome Back</h1>
        <p class="text-sm text-muted mt-1">{{ route.query.verified === '1' ? 'Your email is verified. Sign in to continue.' : route.query.created === '1' ? 'Your account was created. Sign in to continue.' : route.query.reason === 'exists' ? 'An account with this email already exists. Sign in to continue.' : route.query.reason === 'expired' ? 'Your session expired. Sign in again to continue.' : route.query.redirect === '/checkout' ? 'Sign in to continue to checkout. Your cart will be kept.' : 'Sign in to track orders, save addresses, and check out faster' }}</p>
      </div>

      <div v-if="route.query.reason === 'exists'" role="status" class="mb-5 rounded-xl bg-primary/25 px-4 py-3 text-sm text-dark">
        You already have an account with us. Don&apos;t remember your password?
        <button type="button" class="font-semibold underline underline-offset-4 ml-1" @click="goToForgotPassword">
          Reset your password
        </button>
      </div>

      <GoogleSignInButton
        mode="signin"
        :disabled="loading"
        class="mb-4"
        @credential="handleGoogleLogin"
        @error="(msg) => { error = msg }"
      />

      <form novalidate @submit.prevent="handleLogin" class="space-y-4">
        <BaseInput
          v-model="email"
          label="Email"
          type="email"
          required
          id="login-email"
          autocomplete="email"
          :error="fieldErrors.email"
        />
        <BaseInput
          v-model="password"
          label="Password"
          type="password"
          required
          id="login-password"
          autocomplete="current-password"
          :error="fieldErrors.password"
        />

        <div class="flex justify-end">
          <router-link :to="{ path: '/auth/forgot-password', state: email.trim() ? { email: email.trim() } : undefined }" class="text-xs text-muted hover:text-dark">
            Forgot password?
          </router-link>
        </div>

        <p v-if="error" role="alert" class="text-sm text-red-700">{{ error }}</p>

        <BaseButton type="submit" variant="secondary" fullWidth :loading="loading">
          Sign In
        </BaseButton>
      </form>


      <p class="text-sm text-center text-muted mt-6">
        Don&apos;t have an account?
          <router-link :to="{ path: '/auth/register', query: route.query.redirect ? { redirect: route.query.redirect } : {} }" class="text-dark font-medium hover:underline">
          Create one
        </router-link>
      </p>
    </div>
  </div>
</template>
