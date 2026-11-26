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

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const cartStore = useCartStore()
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const fieldErrors = ref<Record<string, string>>({})

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
        <p class="text-sm text-muted mt-1">{{ route.query.verified === '1' ? 'Your email is verified. Sign in to continue.' : route.query.created === '1' ? 'Your account was created. Sign in to continue.' : route.query.reason === 'expired' ? 'Your session expired. Sign in again to continue.' : route.query.redirect === '/checkout' ? 'Sign in to continue to checkout. Your cart will be kept.' : 'Sign in to track orders, save addresses, and check out faster' }}</p>
      </div>

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
          <router-link to="/auth/forgot-password" class="text-xs text-muted hover:text-dark">
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
