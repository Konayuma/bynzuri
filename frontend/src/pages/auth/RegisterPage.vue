<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import axios from 'axios'
import { isEmail, isValidName } from '@/utils/formValidation'
import { getCountryCallingCode, parsePhoneNumberFromString, type CountryCode } from 'libphonenumber-js'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import PhoneInput from '@/components/base/PhoneInput.vue'
import GoogleSignInButton from '@/components/auth/GoogleSignInButton.vue'
import { rememberVerificationEmail } from '@/services/verification-context'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const cartStore = useCartStore()
const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
})
const loading = ref(false)
const error = ref('')
const offerVerification = ref(false)
const fieldErrors = ref<Record<string, string>>({})
const phoneCountry = ref<CountryCode>('ZM')
const safeRedirectQuery = computed(() => {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
  return redirect.startsWith('/') && !redirect.startsWith('//') ? { redirect } : {}
})
watch(phoneCountry, () => { delete fieldErrors.value.phone; error.value = '' })
for (const key of Object.keys(form.value) as Array<keyof typeof form.value>) {
  watch(() => form.value[key], () => {
    delete fieldErrors.value[key]
    error.value = ''
  })
}

async function handleGoogleAuth(credential: string) {
  if (loading.value) return
  loading.value = true
  error.value = ''
  try {
    await userStore.loginWithGoogle(credential)
  } catch (cause) {
    error.value = axios.isAxiosError(cause) && typeof cause.response?.data?.detail === 'string'
      ? cause.response.data.detail
      : 'We could not sign you up with Google. Please try again.'
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
  await router.push(safeRedirectQuery.value.redirect || '/')
}

async function handleRegister() {
  if (loading.value) return
  const data = form.value
  const errors: Record<string, string> = {}
  if (!data.first_name.trim()) errors.first_name = 'Enter your first name.'
  else if (!isValidName(data.first_name)) errors.first_name = 'Enter a valid first name (at least 2 letters).'
  if (!data.last_name.trim()) errors.last_name = 'Enter your last name.'
  else if (!isValidName(data.last_name)) errors.last_name = 'Enter a valid last name (at least 2 letters).'
  if (!isEmail(data.email)) errors.email = 'Enter a valid email address.'
  const rawPhone = data.phone.trim()
  const compactDigits = rawPhone.replace(/[\s().-]/g, '')
  const dialCode = getCountryCallingCode(phoneCountry.value)
  let phone = parsePhoneNumberFromString(rawPhone, phoneCountry.value)
  if ((!phone || !phone.isValid()) && /^\d+$/.test(compactDigits) && compactDigits.startsWith(dialCode)) {
    phone = parsePhoneNumberFromString(`+${compactDigits}`, phoneCountry.value)
  }
  if (!phone || !phone.isValid() || (phone.country && phone.country !== phoneCountry.value)) errors.phone = 'Enter a valid number for the selected country.'
  fieldErrors.value = errors
  if (Object.keys(errors).length) return

  loading.value = true
  error.value = ''
  offerVerification.value = false

  try {
    await userStore.register({
      email: form.value.email.trim(),
      first_name: form.value.first_name.trim(),
      last_name: form.value.last_name.trim(),
      phone: phone!.number
    })
  } catch (cause) {
    const errorCode = axios.isAxiosError(cause) && typeof cause.response?.data?.code === 'string'
      ? cause.response.data.code
      : ''
    const enteredEmail = form.value.email.trim()
    if (errorCode === 'account_exists') {
      loading.value = false
      await router.push({
        path: '/auth/login',
        state: { email: enteredEmail },
        query: { ...safeRedirectQuery.value, reason: 'exists' }
      })
      return
    }
    if (errorCode === 'unverified_account_exists') {
      rememberVerificationEmail(enteredEmail)
      loading.value = false
      await router.push({
        path: '/auth/verify-email',
        state: { email: enteredEmail },
        query: safeRedirectQuery.value
      })
      return
    }
    error.value = axios.isAxiosError(cause) && cause.response?.status === 400
      ? 'Check your details. If you already have an account, sign in or verify your email.'
      : 'We could not create your account. Check your connection and try again.'
    offerVerification.value = true
    loading.value = false
    return
  }

  const registeredEmail = form.value.email.trim()
  rememberVerificationEmail(registeredEmail)
  loading.value = false
  await router.push({
    path: '/auth/verify-email',
    state: { email: registeredEmail },
    query: safeRedirectQuery.value
  })
}
function continueVerification() {
  const email = form.value.email.trim()
  if (!isEmail(email)) {
    fieldErrors.value.email = 'Enter a valid email address.'
    return
  }
  rememberVerificationEmail(email)
  void router.push({ path: '/auth/verify-email', state: { email }, query: safeRedirectQuery.value })
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center px-4 py-12">
    <div class="w-full max-w-md mx-auto">
      <div class="text-center mb-8">
        <h1 class="font-heading text-2xl sm:text-3xl font-semibold text-dark">Create Account</h1>
        <p class="text-sm text-muted mt-1.5">Track your orders, save addresses, and shop faster next time</p>
      </div>

      <GoogleSignInButton
        mode="signup"
        :disabled="loading"
        class="mb-4"
        @credential="handleGoogleAuth"
        @error="(msg) => { error = msg }"
      />

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
        <PhoneInput v-model="form.phone" v-model:country="phoneCountry" :error="fieldErrors.phone" :disabled="loading" />

        <p v-if="error" role="alert" class="text-sm text-red-700">{{ error }}</p>

        <div v-if="offerVerification" class="text-sm text-muted">
          If you already started creating an account, continue to verification and request a new code if needed.
          <button type="button" class="text-dark font-medium underline" @click="continueVerification">Continue verification</button>
        </div>

        <BaseButton type="submit" variant="secondary" fullWidth :loading="loading">
          Continue
        </BaseButton>
      </form>

      <p class="text-sm text-center text-muted mt-6">
        Already have an account?
        <router-link :to="{ path: '/auth/login', query: safeRedirectQuery }" class="text-dark font-medium hover:underline">
          Sign in
        </router-link>
      </p>
    </div>
  </div>
</template>
