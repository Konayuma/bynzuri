<script setup lang="ts">
import { ref } from 'vue'
import { authService } from '@/services/auth.service'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'

const email = ref('')
const loading = ref(false)
const error = ref('')
const sent = ref(false)

async function handleForgotPassword() {
  if (!email.value) {
    error.value = 'Enter your email address'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await authService.forgotPassword(email.value, `${window.location.origin}/auth/reset-password`)
    sent.value = true
  } catch {
    error.value = 'Something went wrong. Please try again.'
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
          Enter the email you used to sign up and we&apos;ll send you a reset link
        </p>
        <p v-else class="text-sm text-muted mt-1">
          Check your inbox for a reset link. It may take a minute to arrive.
        </p>
      </div>

      <form v-if="!sent" @submit.prevent="handleForgotPassword" class="space-y-4">
        <BaseInput
          v-model="email"
          label="Email"
          type="email"
          required
          id="forgot-email"
        />

        <p v-if="error" class="text-xs text-red-500">{{ error }}</p>

        <BaseButton type="submit" variant="secondary" fullWidth :loading="loading">
          Send Reset Link
        </BaseButton>
      </form>

      <BaseButton v-else variant="secondary" fullWidth @click="$router.push('/auth/login')">
        Back to Sign In
      </BaseButton>

      <p class="text-sm text-center text-muted mt-6">
        Remember your password?
        <router-link to="/auth/login" class="text-dark font-medium hover:underline">
          Sign in
        </router-link>
      </p>
    </div>
  </div>
</template>
