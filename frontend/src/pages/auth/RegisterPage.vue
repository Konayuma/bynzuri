<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import axios from 'axios'
import { isEmail, isValidName, validatePassword } from '@/utils/formValidation'
import { getCountryCallingCode, parsePhoneNumberFromString, type CountryCode } from 'libphonenumber-js'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import PhoneInput from '@/components/base/PhoneInput.vue'
import { rememberSignupCredentials, rememberVerificationEmail } from '@/services/verification-context'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  password: '',
  confirm_password: ''
})
const loading = ref(false)
const error = ref('')
const fieldErrors = ref<Record<string, string>>({})
const phoneCountry = ref<CountryCode>('ZM')
const passwordCheck = computed(() => validatePassword(form.value.password))
watch(phoneCountry, () => { delete fieldErrors.value.phone; error.value = '' })
for (const key of Object.keys(form.value) as Array<keyof typeof form.value>) {
  watch(() => form.value[key], () => {
    delete fieldErrors.value[key]
    error.value = ''
  })
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
  const pw = validatePassword(data.password)
  if (!pw.valid) errors.password = pw.message
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
      phone: phone!.number
    })
  } catch (cause) {
    error.value = axios.isAxiosError(cause) && cause.response?.status === 400
      ? 'Check your details. If you already have an account, sign in or verify your email.'
      : 'We could not create your account. Check your connection and try again.'
    loading.value = false
    return
  }

  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
  const registeredEmail = form.value.email.trim()
  rememberVerificationEmail(registeredEmail)
  rememberSignupCredentials(registeredEmail, form.value.password)
  form.value.password = ''
  form.value.confirm_password = ''
  loading.value = false
  await router.push({
    path: '/auth/verify-email',
    state: { email: registeredEmail },
    query: { ...(redirect.startsWith('/') && !redirect.startsWith('//') ? { redirect } : {}) }
  })
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center px-4 py-12">
    <div class="w-full max-w-md mx-auto">
      <div class="text-center mb-8">
        <h1 class="font-heading text-2xl sm:text-3xl font-semibold text-dark">Create Account</h1>
        <p class="text-sm text-muted mt-1.5">Track your orders, save addresses, and shop faster next time</p>
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
        <PhoneInput v-model="form.phone" v-model:country="phoneCountry" :error="fieldErrors.phone" :disabled="loading" />
        <BaseInput
          v-model="form.password"
          label="Password"
          type="password"
          required
          id="reg-password"
            :error="fieldErrors.password"
            autocomplete="new-password"
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
