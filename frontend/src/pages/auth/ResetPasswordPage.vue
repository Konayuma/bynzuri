<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authService } from '@/services/auth.service'
import { validatePassword } from '@/utils/formValidation'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'

const route = useRoute()
const router = useRouter()
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const fieldErrors = ref<Record<string, string>>({})
const success = ref(false)
const uid = ref('')
const token = ref('')

const passwordCheck = computed(() => validatePassword(newPassword.value))

watch(newPassword, () => { delete fieldErrors.value.newPassword; error.value = '' })
watch(confirmPassword, () => { delete fieldErrors.value.confirmPassword; error.value = '' })

onMounted(() => {
  uid.value = (route.query.uid as string) || ''
  token.value = (route.query.token as string) || ''
  if (!uid.value || !token.value) {
    error.value = 'Invalid reset link'
  }
})

async function handleResetPassword() {
  const errors: Record<string, string> = {}
  if (!newPassword.value || !confirmPassword.value) {
    if (!newPassword.value) errors.newPassword = 'Enter a new password.'
    if (!confirmPassword.value) errors.confirmPassword = 'Confirm your new password.'
    fieldErrors.value = errors
    error.value = 'Enter both password fields'
    return
  }
  const pw = validatePassword(newPassword.value)
  if (!pw.valid) {
    fieldErrors.value = { newPassword: pw.message }
    error.value = pw.message
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    fieldErrors.value = { confirmPassword: "Passwords don't match." }
    error.value = "Passwords don't match"
    return
  }
  fieldErrors.value = {}

  loading.value = true
  error.value = ''

  try {
    await authService.resetPassword(uid.value, token.value, newPassword.value)
    success.value = true
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    error.value = detail || 'Reset link is invalid or has expired'
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

      <form v-if="!success" novalidate @submit.prevent="handleResetPassword" class="space-y-4">
        <BaseInput
          v-model="newPassword"
          label="New Password"
          type="password"
          required
          id="reset-password"
          autocomplete="new-password"
          :error="fieldErrors.newPassword"
        />
        <ul class="text-xs space-y-1 -mt-2 text-muted" aria-label="Password requirements">
          <li :class="passwordCheck.checks.minLength ? 'text-success font-medium' : ''">
            {{ passwordCheck.checks.minLength ? '✓' : '•' }} At least 8 characters
          </li>
          <li :class="passwordCheck.checks.hasLetter && passwordCheck.checks.hasNumber ? 'text-success font-medium' : ''">
            {{ passwordCheck.checks.hasLetter && passwordCheck.checks.hasNumber ? '✓' : '•' }} Includes a letter and a number
          </li>
        </ul>
        <BaseInput
          v-model="confirmPassword"
          label="Confirm Password"
          type="password"
          required
          id="reset-confirm"
          autocomplete="new-password"
          :error="fieldErrors.confirmPassword"
        />

        <p v-if="error" role="alert" class="text-sm text-red-700">{{ error }}</p>

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
