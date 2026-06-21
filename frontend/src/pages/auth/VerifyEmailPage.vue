<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authService } from '@/services/auth.service'
import BaseButton from '@/components/base/BaseButton.vue'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const error = ref('')
const success = ref(false)

onMounted(async () => {
  const token = route.query.token as string
  if (!token) {
    error.value = 'Invalid verification link'
    loading.value = false
    return
  }

  try {
    await authService.verifyEmail(token)
    success.value = true
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Verification link is invalid or has expired'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center px-4">
    <div class="w-full max-w-sm text-center">
      <div v-if="loading" class="py-8">
        <div class="animate-spin w-8 h-8 border-2 border-dark border-t-transparent rounded-full mx-auto"></div>
        <p class="text-sm text-muted mt-4">Verifying your email...</p>
      </div>

      <template v-else>
        <h1 class="font-heading text-2xl font-semibold text-dark">
          {{ success ? 'Email Verified' : 'Verification Failed' }}
        </h1>
        <p class="text-sm text-muted mt-2">
          {{ success
            ? 'Your email has been verified. You can now use all features of your account.'
            : error
          }}
        </p>
        <BaseButton
          variant="secondary"
          fullWidth
          class="mt-6"
          @click="router.push(success ? '/auth/login' : '/')"
        >
          {{ success ? 'Sign In' : 'Go Home' }}
        </BaseButton>
      </template>
    </div>
  </div>
</template>
