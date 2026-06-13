<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'

const router = useRouter()
const userStore = useUserStore()
const cartStore = useCartStore()
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  if (!email.value || !password.value) {
    error.value = 'Please fill in all fields'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await userStore.login(email.value, password.value)
    await cartStore.mergeGuestCart()
    await cartStore.fetchCart()
    router.push('/')
  } catch {
    error.value = 'Invalid email or password'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center px-4">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <h1 class="font-heading text-2xl font-semibold text-dark">Welcome Back</h1>
        <p class="text-sm text-muted mt-1">Sign in to your By Nzuri account</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <BaseInput
          v-model="email"
          label="Email"
          type="email"
          required
          id="login-email"
        />
        <BaseInput
          v-model="password"
          label="Password"
          type="password"
          required
          id="login-password"
        />

        <p v-if="error" class="text-xs text-red-500">{{ error }}</p>

        <BaseButton type="submit" variant="secondary" fullWidth :loading="loading">
          Sign In
        </BaseButton>
      </form>

      <p class="text-sm text-center text-muted mt-6">
        Don&apos;t have an account?
        <router-link to="/auth/register" class="text-dark font-medium hover:underline">
          Create one
        </router-link>
      </p>
    </div>
  </div>
</template>
