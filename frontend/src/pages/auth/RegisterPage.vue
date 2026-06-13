<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'

const router = useRouter()
const userStore = useUserStore()
const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '260',
  password: '',
  confirm_password: ''
})
const loading = ref(false)
const error = ref('')

async function handleRegister() {
  if (form.value.password !== form.value.confirm_password) {
    error.value = 'Passwords do not match'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await userStore.register({
      email: form.value.email,
      password: form.value.password,
      first_name: form.value.first_name,
      last_name: form.value.last_name,
      phone: form.value.phone
    })
    await userStore.login(form.value.email, form.value.password)
    router.push('/')
  } catch {
    error.value = 'Registration failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center px-4">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <h1 class="font-heading text-2xl font-semibold text-dark">Create Account</h1>
        <p class="text-sm text-muted mt-1">Join the By Nzuri beauty circle</p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <div class="grid grid-cols-2 gap-3">
          <BaseInput
            v-model="form.first_name"
            label="First Name"
            required
            id="reg-first"
          />
          <BaseInput
            v-model="form.last_name"
            label="Last Name"
            required
            id="reg-last"
          />
        </div>
        <BaseInput
          v-model="form.email"
          label="Email"
          type="email"
          required
          id="reg-email"
        />
        <BaseInput
          v-model="form.phone"
          label="Phone"
          type="tel"
          required
          id="reg-phone"
        />
        <BaseInput
          v-model="form.password"
          label="Password"
          type="password"
          required
          id="reg-password"
        />
        <BaseInput
          v-model="form.confirm_password"
          label="Confirm Password"
          type="password"
          required
          id="reg-confirm"
        />

        <p v-if="error" class="text-xs text-red-500">{{ error }}</p>

        <BaseButton type="submit" variant="secondary" fullWidth :loading="loading">
          Create Account
        </BaseButton>
      </form>

      <p class="text-sm text-center text-muted mt-6">
        Already have an account?
        <router-link to="/auth/login" class="text-dark font-medium hover:underline">
          Sign in
        </router-link>
      </p>
    </div>
  </div>
</template>
