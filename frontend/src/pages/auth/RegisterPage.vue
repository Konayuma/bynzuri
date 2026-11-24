<script setup lang="ts">
import { ref, watch } from 'vue'
import { isEmail, isZambianPhone } from '@/utils/formValidation'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const cartStore = useCartStore()
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
const fieldErrors = ref<Record<string, string>>({})
for (const key of Object.keys(form.value) as Array<keyof typeof form.value>) {
  watch(() => form.value[key], () => {
    delete fieldErrors.value[key]
    error.value = ''
  })
}

async function handleRegister() {
  const data = form.value
  const errors: Record<string, string> = {}
  if (!data.first_name.trim()) errors.first_name = 'Enter your first name.'
  if (!data.last_name.trim()) errors.last_name = 'Enter your last name.'
  if (!isEmail(data.email)) errors.email = 'Enter a valid email address.'
  if (!isZambianPhone(data.phone)) errors.phone = 'Enter a Zambian number, for example 0971234567 or +260971234567.'
  if (data.password.length < 8) errors.password = 'Use at least 8 characters.'
  if (data.password !== data.confirm_password) errors.confirm_password = 'Passwords do not match.'
  fieldErrors.value = errors
  if (Object.keys(errors).length) return

  loading.value = true
  error.value = ''

  try {
    await userStore.register({
      email: form.value.email.trim(),
      password: form.value.password,
      first_name: form.value.first_name.trim(),
      last_name: form.value.last_name.trim(),
      phone: form.value.phone
    })
  } catch {
    error.value = 'Could not create your account. The email may already be in use.'
    loading.value = false
    return
  }

  try {
    await userStore.login(form.value.email.trim(), form.value.password)
  } catch {
    loading.value = false
    await router.push({ path: '/auth/login', query: { ...route.query, created: '1' } })
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
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center px-4">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <h1 class="font-heading text-2xl font-semibold text-dark">Create Account</h1>
        <p class="text-sm text-muted mt-1">Track your orders, save addresses, and shop faster next time</p>
      </div>

      <form novalidate @submit.prevent="handleRegister" class="space-y-4">
        <div class="grid grid-cols-2 gap-3">
          <BaseInput
            v-model="form.first_name"
            label="First Name"
            required
            id="reg-first"
            :error="fieldErrors.first_name"
            autocomplete="given-name"
          />
          <BaseInput
            v-model="form.last_name"
            label="Last Name"
            required
            id="reg-last"
            :error="fieldErrors.last_name"
            autocomplete="family-name"
          />
        </div>
        <BaseInput
          v-model="form.email"
          label="Email"
          type="email"
          required
          id="reg-email"
            :error="fieldErrors.email"
            autocomplete="email"
        />
        <BaseInput
          v-model="form.phone"
          label="Phone Number"
          type="tel"
          required
          id="reg-phone"
            :error="fieldErrors.phone"
            autocomplete="tel"
          placeholder="260xxxxxxxxx"
        />
        <p class="text-xs text-muted -mt-2">Zambian mobile number for delivery updates</p>
        <BaseInput
          v-model="form.password"
          label="Password"
          type="password"
          required
          id="reg-password"
            :error="fieldErrors.password"
            autocomplete="new-password"
        />
        <p class="text-xs text-muted -mt-2">At least 8 characters</p>
        <BaseInput
          v-model="form.confirm_password"
          label="Confirm Password"
          type="password"
          required
          id="reg-confirm"
            :error="fieldErrors.confirm_password"
            autocomplete="new-password"
        />

        <p v-if="error" role="alert" class="text-sm text-red-700">{{ error }}</p>

        <BaseButton type="submit" variant="secondary" fullWidth :loading="loading">
          Create Account
        </BaseButton>
      </form>

      <p class="text-sm text-center text-muted mt-6">
        Already have an account?
        <router-link :to="{ path: '/auth/login', query: route.query.redirect ? { redirect: route.query.redirect } : {} }" class="text-dark font-medium hover:underline">
          Sign in
        </router-link>
      </p>
    </div>
  </div>
</template>
