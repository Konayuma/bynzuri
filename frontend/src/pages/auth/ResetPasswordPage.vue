<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authService } from '@/services/auth.service'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'

const route = useRoute()
const router = useRouter()
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)
const uid = ref('')
const token = ref('')

onMounted(() => {
  uid.value = (route.query.uid as string) || ''
  token.value = (route.query.token as string) || ''
  if (!uid.value || !token.value) {
    error.value = 'Invalid reset link'
  }
})

async function handleResetPassword() {
  if (!newPassword.value || !confirmPassword.value) {
    error.value = 'Enter both password fields'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Passwords don\'t match'
    return
  }
  if (newPassword.value.length < 8) {
    error.value = 'Password must be at least 8 characters'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await authService.resetPassword(uid.value, token.value, newPassword.value)
    success.value = true
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Reset link is invalid or has expired'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center px-4">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <h1 class="font-heading text-2xl font-semibold text-dark">New Password</h1>
        <p v-if="!success" class="text-sm text-muted mt-1">
          Enter your new password below
        </p>
        <p v-else class="text-sm text-muted mt-1">
          Your password has been reset successfully
        </p>
      </div>

      <form v-if="!success" @submit.prevent="handleResetPassword" class="space-y-4">
        <BaseInput
          v-model="newPassword"
          label="New Password"
          type="password"
          required
          id="reset-password"
        />
        <p class="text-xs text-muted -mt-2">At least 8 characters</p>
        <BaseInput
          v-model="confirmPassword"
          label="Confirm Password"
          type="password"
          required
          id="reset-confirm"
        />

        <p v-if="error" class="text-xs text-red-500">{{ error }}</p>

        <BaseButton type="submit" variant="secondary" fullWidth :loading="loading" :disabled="!uid || !token">
          Reset Password
        </BaseButton>
      </form>

      <BaseButton v-else variant="secondary" fullWidth @click="router.push('/auth/login')">
        Sign In with New Password
      </BaseButton>

      <p class="text-sm text-center text-muted mt-6">
        <router-link to="/auth/login" class="text-dark font-medium hover:underline">
          Back to Sign In
        </router-link>
      </p>
    </div>
  </div>
</template>
